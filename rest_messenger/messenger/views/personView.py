from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets

from messenger.models.person import Person
from messenger.serializers.personSerializers import PersonSerializer


@method_decorator(name="create", decorator=swagger_auto_schema(
    operation_summary="Create new Person",
    operation_description=':param request: body: {'
                          '  "name": "string"'
                          '}'
))
@method_decorator(name="retrieve", decorator=swagger_auto_schema(
    operation_summary="Get Person info",
    operation_description=':param request: path: {'
                          '  "id": "uuid"'
                          '}'
))
class PersonViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    Basic create and get methods
    """
    serializer_class = PersonSerializer
    queryset = Person.objects.all()
