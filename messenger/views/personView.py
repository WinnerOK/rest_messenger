from rest_framework import mixins, viewsets

from messenger.models.person import Person
from messenger.serializers.personSerializers import PersonSerializer


class PersonViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = PersonSerializer
    queryset = Person.objects.all()