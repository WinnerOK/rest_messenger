from rest_framework import serializers, status
from rest_framework.response import Response

from .models import Person, Message


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["id", "name"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["text", "sender", "receiver", "created_at", "updated_at"]


# =========================================================================
def is_same_sender(instance, validated_data):
    return instance.sender == validated_data["sender"]


class MessageUpdateSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        if is_same_sender(instance, validated_data):
            instance.text = validated_data["text"]
            instance.save()
            return instance
        else:
            raise serializers.ValidationError(
                {"detail": "Updating someone else's message is prohibited"}
            )

    class Meta:
        model = Message
        fields = ["text", "sender", "receiver", "created_at", "updated_at"]
        read_only_fields = ["receiver", "created_at", "updated_at"]


class MessageDestroySerializer(serializers.ModelSerializer):

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    class Meta:
        model = Message
        fields = ["text", "sender", "receiver", "created_at", "updated_at"]
        read_only_fields = ["receiver", "created_at", "updated_at"]