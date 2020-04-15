from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Person, Message
from .serializers import PersonSerializer, MessageSerializer, MessageUpdateSerializer, MessageDestroySerializer, \
    UserAuthenticationSerializer


class PersonViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = PersonSerializer
    queryset = Person.objects.all()


class MessageView(mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
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
def message_get(request):
    person = validate_person(request.data)
    # sent = Message.objects.filter(sender__id__exact=person.id)
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
def message_get(request):
    person = validate_person(request.data)
    sent = Message.objects.filter(sender__id__exact=person.id).order_by("created_at")
    out = MessageSerializer(data=sent, many=True)
    out.is_valid()
    return Response(out.data)


class PingView(APIView):
    def get(self, request):
        return JsonResponse({"pong": True})
