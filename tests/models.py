from __future__ import annotations

from uuid import UUID

import timeflake
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


def generate_timeflake() -> UUID:
    """Generate UUID for models uid fields."""
    return timeflake.random().uuid


class User(AbstractUser):
    id = models.UUIDField(verbose_name=_('ID'), primary_key=True, blank=True, default=generate_timeflake, editable=False)
    email = models.EmailField(_('E-mail address'), unique=True)

    class Meta:
        get_latest_by = 'id'
