from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from .utils import generate_timeflake


class MagicLink(models.Model):  # type: ignore
    id = models.UUIDField(verbose_name='ID', primary_key=True, blank=True, default=generate_timeflake, editable=False)
    email = models.EmailField(verbose_name=_('email address'), unique=True)
    date_created = models.DateTimeField(_('date created'), auto_now_add=True, db_index=True)

    def __str__(self) -> str:
        return '{pk} - {email}'.format(pk=str(self.pk), email=self.email)
