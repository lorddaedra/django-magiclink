from typing import Optional
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

    @staticmethod
    def used(ml: 'MagicLink') -> None:
        ml.times_used += 1
        if ml.times_used >= settings.TOKEN_USES:
            ml.disabled = True
        ml.save()

    @staticmethod
    def disable(ml: 'MagicLink') -> None:
        ml.times_used += 1
        ml.disabled = True
        ml.save()

    @staticmethod
    def generate_url(token: str, email: str, request: HttpRequest) -> str:
        url_path = reverse("magiclink:login_verify")

        params = {'token': token}
        if settings.VERIFY_INCLUDE_EMAIL:
            params['email'] = email
        query = urlencode(params)

        url_path = f'{url_path}?{query}'
        domain = get_current_site(request).domain
        scheme = request.is_secure() and "https" or "http"
        url = urljoin(f'{scheme}://{domain}', url_path)
        return url

    @staticmethod
    def send(ml: 'MagicLink', request: HttpRequest, style: Optional[dict[str, str]] = None) -> None:
        user = User.objects.get(email=ml.email)
        context = {
            'subject': settings.EMAIL_SUBJECT,
            'user': user,
            'magiclink': MagicLink.generate_url(token=ml.token, email=ml.email, request=request),
            'expiry': ml.expiry,
            'ip_address': ml.ip_address,
            'created': ml.created,
            'token_uses': settings.TOKEN_USES,
            'style': style if style else {
                'logo_url': '',
                'background_color': '#ffffff',
                'main_text_color': '#000000',
                'button_background_color': '#0078be',
                'button_text_color': '#ffffff',
            },
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
            MagicLink.disable(ml)
            raise MagicLinkError('Magic link has expired')

        if ml.times_used >= settings.TOKEN_USES:
            MagicLink.disable(ml)
            raise MagicLinkError('Magic link has been used too many times')

        user = User.objects.get(email=ml.email)

        return user
