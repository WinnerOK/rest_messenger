from rest_framework import serializers

from messenger.models.person import Person


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["id", "name"]


class UserAuthenticationSerializer(serializers.Serializer):  # noqa
    user = serializers.UUIDField()