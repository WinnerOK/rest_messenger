from django.http import JsonResponse
from rest_framework import viewsets, mixins
from rest_framework.views import APIView

from .models import Person, Message
from .serializers import PersonSerializer, MessageSerializer, MessageUpdateSerializer, MessageDestroySerializer


class PersonViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = PersonSerializer
    queryset = Person.objects.all()


class MessageView(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Message.objects.all()

    def get_serializer_class(self):
        if hasattr(self, "action"):
            if self.action == 'update':
                return MessageUpdateSerializer
            elif self.action == 'destroy':
                return MessageDestroySerializer

        return MessageSerializer


class PingView(APIView):
    def get(self, request):
        return JsonResponse({"pong": True})
