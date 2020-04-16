from rest_framework import serializers, status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response

from messenger.models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "text", "sender", "receiver", "created_at", "updated_at"]


class MessageUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for partial update.
    Update message if appropriate sender is passed
    """
    def update(self, instance, validated_data):
        if instance.sender == validated_data["sender"]:
            instance.text = validated_data["text"]
            instance.save()
            return instance
        else:
            raise NotAuthenticated(
                {"detail": "Updating someone else's message is prohibited"}
            )

    class Meta:
        model = Message
        fields = ["id", "text", "sender", "receiver", "created_at", "updated_at"]
        read_only_fields = ["receiver", "created_at", "updated_at"]


class MessageDestroySerializer(serializers.ModelSerializer):
    """
    Destroy message if its sender is passed
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sender == self.validated_data["sender"]:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):  # noqa
        instance.delete()

    class Meta:
        model = Message
        fields = ["id", "text", "sender", "receiver", "created_at", "updated_at"]
        read_only_fields = ["receiver", "created_at", "updated_at"]
