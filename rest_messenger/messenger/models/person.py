import uuid

from django.db import models


class Person(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )
    name = models.CharField(
        max_length=25,
        null=False
    )
