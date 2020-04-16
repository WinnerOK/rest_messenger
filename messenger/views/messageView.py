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


# According to RFC, request body must be ignored in GET, DELETE methods, so I replaced them with POST
class MessageView(mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    queryset = Message.objects.all()

    def get_serializer_class(self):
        if hasattr(self, "action"):
            if self.action == 'partial_update':
                return MessageUpdateSerializer
            elif self.action == 'destroy':
                return MessageDestroySerializer

        return MessageSerializer

    def partial_update(self, request, *args, **kwargs):
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


def validate_person(request_data) -> Person:
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
def message_get_received(request):
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
def message_destroy(request, pk, *args, **kwargs):
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
