from typing import Dict

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.response import Response

from messenger.models import Message
from messenger.models.person import Person
from messenger.serializers.messageSerializers import MessageUpdateSerializer, MessageDestroySerializer, \
    MessageSerializer
from messenger.serializers.personSerializers import UserAuthenticationSerializer

"""
Big problem with messages is a desire to authenticate user by id sent with every request in body.

It will be better to create custom authorization class in Django which will be responsible for user authentication
by id in cookie or header, so that we get rid of 'hacking' default in-built serializers and mixins. 
"""


@method_decorator(name="create", decorator=swagger_auto_schema(
    operation_summary="Create new message",
    operation_description=':param request: body: {'
                          '  "text": "string",'
                          '  "sender": "uuid",'
                          '  "receiver": "uuid"'
                          '}'
))
class MessageView(mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    """
    Since we have to proceed id in body, I left standard Creation mixin and a partial update.
    """
    queryset = Message.objects.all()

    def get_serializer_class(self):
        if hasattr(self, "action"):
            if self.action == 'partial_update':
                return MessageUpdateSerializer

        return MessageSerializer

    def partial_update(self, request, *args, **kwargs):
        """
        Update message text given uuid of message and uuid of sender

        :param request: body: {"sender": "uuid", "text": "string"}
        :return:
        """
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


def validate_person(request_data: Dict[str, str]) -> Person:
    """
    Return Person object from the DB if exists, otherwise NotAuthenticated raised/

    :param request_data: {"user": "uuid"}
    :return: corresponding Person object
    """
    serializer = UserAuthenticationSerializer(data=request_data)
    serializer.is_valid(raise_exception=True)
    person = Person.objects.filter(id=serializer.validated_data["user"]).first()
    if person is None:
        raise NotAuthenticated(detail="User with given uuid doesn't exist")
    return person


@swagger_auto_schema(
    method='POST',
    request_body=UserAuthenticationSerializer,
    responses={200: MessageSerializer},
    operation_id="messages_receive",
)
@api_view(["POST"])
# Body in GET and DELETE requests should be ignored, I decided to make post request for this and following ops.
def message_get_received(request):
    """
    Return all messages received by person with given in body uuid.

    :param request: user request with {"user": "uuid"} inside body
    """
    person = validate_person(request.data)
    received = Message.objects.filter(receiver__id__exact=person.id).order_by("created_at")
    out = MessageSerializer(data=received, many=True)
    out.is_valid()
    return Response(out.data)


@swagger_auto_schema(
    method='POST',
    request_body=UserAuthenticationSerializer,
    responses={200: MessageSerializer},
    operation_id="messages_sent",
)
@api_view(["POST"])
def message_get_sent(request):
    """
    Return all messages sent by person with given in body uuid.

    :param request: user request with {"user": "uuid"} inside body
    """
    person = validate_person(request.data)
    sent = Message.objects.filter(sender__id__exact=person.id).order_by("created_at")
    out = MessageSerializer(data=sent, many=True)
    out.is_valid()
    return Response(out.data)


@swagger_auto_schema(
    method='POST',
    request_body=UserAuthenticationSerializer,
    responses={200: MessageSerializer},
    operation_id="messages_destroy",
)
@api_view(["POST"])
def message_destroy(request, pk):
    """
    Remove message from the DB if sender requested deletion.

    :param request: user request with {"user": "uuid"} inside body
    :param pk: primary key of Message
    """
    person = validate_person(request.data)
    if person is None:
        raise NotAuthenticated(detail="User with given uuid doesn't exist")

    message = Message.objects.filter(id__exact=pk).first()
    if message is None:
        raise NotFound(detail="Message with given uuid doesn't exist")

    if person.id == message.sender.id:
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        raise NotAuthenticated(detail="Deleting other's messages is prohibited")
