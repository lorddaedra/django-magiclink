from urllib.parse import urlencode, urljoin

from django.conf import settings as djsettings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import models
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from . import settings

User = get_user_model()


class MagicLinkError(Exception):
    pass


class MagicLink(models.Model):
    email = models.EmailField()
    token = models.TextField()
    expiry = models.DateTimeField()
    redirect_url = models.TextField()
    disabled = models.BooleanField(default=False)
    times_used = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email} - {self.expiry}'

    def used(self) -> None:
        self.times_used += 1
        if self.times_used >= settings.TOKEN_USES:
            self.disabled = True
        self.save()

    def disable(self) -> None:
        self.times_used += 1
        self.disabled = True
        self.save()

    def generate_url(self, request: HttpRequest) -> str:
        url_path = reverse("magiclink:login_verify")

        params = {'token': self.token}
        if settings.VERIFY_INCLUDE_EMAIL:
            params['email'] = self.email
        query = urlencode(params)

        url_path = f'{url_path}?{query}'
        domain = get_current_site(request).domain
        scheme = request.is_secure() and "https" or "http"
        url = urljoin(f'{scheme}://{domain}', url_path)
        return url

    def send(self, request: HttpRequest) -> None:
        user = User.objects.get(email=self.email)
        context = {
            'subject': settings.EMAIL_SUBJECT,
            'user': user,
            'magiclink': self.generate_url(request),
            'expiry': self.expiry,
            'ip_address': self.ip_address,
            'created': self.created,
            'token_uses': settings.TOKEN_USES,
            'style': settings.EMAIL_STYLES,
        }
        plain = render_to_string(settings.EMAIL_TEMPLATE_NAME_TEXT, context)
        html = render_to_string(settings.EMAIL_TEMPLATE_NAME_HTML, context)
        send_mail(
            subject=settings.EMAIL_SUBJECT,
            message=plain,
            recipient_list=[user.email],
            from_email=djsettings.DEFAULT_FROM_EMAIL,
            html_message=html,
        )

    @staticmethod
    def validate(ml: 'MagicLink', email: str = '') -> AbstractUser:
        if settings.EMAIL_IGNORE_CASE and email:
            email = email.lower()

        if settings.VERIFY_INCLUDE_EMAIL and ml.email != email:
            raise MagicLinkError('Email address does not match')

        if timezone.now() > ml.expiry:
            ml.disable()
            raise MagicLinkError('Magic link has expired')

        if ml.times_used >= settings.TOKEN_USES:
            ml.disable()
            raise MagicLinkError('Magic link has been used too many times')

        user = User.objects.get(email=ml.email)

        return user
