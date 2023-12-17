"""
Models for user accounts.
"""
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    Uses a UUID as the primary key.

    Attributes:
        uuid (UUIDField): The universally unique identifier for this user.
    """

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    def __str__(self):
        return self.username
