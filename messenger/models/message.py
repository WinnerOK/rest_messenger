import uuid

from django.db import models

from messenger.models.person import Person


class Message(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )
    text = models.TextField(
        max_length=1024,
        null=False
    )
    sender = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="received_messages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
