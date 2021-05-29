from __future__ import annotations

from django.db import models


class MagicLinkError(Exception):
    pass


class MagicLink(models.Model):
    email = models.EmailField()
    token = models.TextField()
    expiry = models.DateTimeField()
    redirect_url = models.TextField()
    disabled = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email} - {self.expiry}'
