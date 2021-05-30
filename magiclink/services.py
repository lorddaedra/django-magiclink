from __future__ import annotations

import logging
from datetime import timedelta
from secrets import token_urlsafe
from typing import Optional
from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from magiclink.models import MagicLink, MagicLinkError
from magiclink.utils import get_url_path

logger = logging.getLogger(__name__)
User = get_user_model()


def create_user(*, email: str) -> None:
    """Create `user`."""
    logger.info('Creating user')
    email = email.lower()
    password: str = make_password(None)
    user = User(email=email, password=password, is_staff=False, is_superuser=False)
    user.username = str(user.pk).replace('-', '')
    user.save()


def create_magiclink(*, email: str, ip_address: str, redirect_url: str = '', limit_seconds: int = 3, expiry_seconds: int = 900) -> MagicLink:
    email = email.lower()

    limit = timezone.now() - timedelta(seconds=limit_seconds)  # NOQA: E501
    over_limit = MagicLink.objects.filter(email=email, date_created__gte=limit)
    if over_limit:
        raise MagicLinkError('Too many magic login requests')

    MagicLink.objects.filter(email=email, disabled=False).update(disabled=True)

    if not redirect_url:
        redirect_url = get_url_path(settings.LOGIN_REDIRECT_URL)

    expiry = timezone.now() + timedelta(seconds=expiry_seconds)
    magic_link = MagicLink.objects.create(email=email, token=token_urlsafe(), expiry=expiry, redirect_url=redirect_url,
                                          ip_address=ip_address)
    return magic_link


def disable_magiclink(*, pk: int) -> None:
    MagicLink.objects.filter(pk=pk).update(disabled=True)


def validate_magiclink(*, ml: 'MagicLink', email: str = '') -> AbstractUser:
    if email:
        email = email.lower()

    if ml.email != email:
        raise MagicLinkError('Email address does not match')

    if timezone.now() > ml.expiry:
        disable_magiclink(pk=ml.pk)
        raise MagicLinkError('Magic link has expired')

    if ml.disabled:
        raise MagicLinkError('Magic link has been used')

    user = User.objects.get(email=ml.email)

    return user


def send_magiclink(*, ml: 'MagicLink', domain: str, subject: str,
                   email_templates: tuple[str, str] = ('magiclink/login_email.txt', 'magiclink/login_email.html'),
                   style: Optional[dict[str, str]] = None) -> None:
    user = User.objects.get(email=ml.email)
    context = {
        'subject': subject,
        'user': user,
        'magiclink': generate_url(token=ml.token, email=ml.email, domain=domain),
        'expiry': ml.expiry,
        'ip_address': ml.ip_address,
        'date_created': ml.date_created,
        'style': style if style else {
            'logo_url': '',
            'background_color': '#ffffff',
            'main_text_color': '#000000',
            'button_background_color': '#0078be',
            'button_text_color': '#ffffff',
        },
    }
    plain = render_to_string(email_templates[0], context)
    html = render_to_string(email_templates[1], context)
    send_mail(
        subject=subject,
        message=plain,
        recipient_list=[user.email],
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=html,
    )


def generate_url(*, token: str, email: str, domain: str) -> str:
    url_path = reverse("magiclink:login_verify")

    params = {'token': token, 'email': email}
    query = urlencode(params)

    url_path = f'{url_path}?{query}'
    url = urljoin(f'https://{domain}', url_path)
    return url
