from __future__ import annotations

import logging
from datetime import timedelta
from typing import Optional, Union
from urllib.parse import urlencode, urljoin
from uuid import UUID

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core import signing
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from magiclinks.exceptions import MagicLinkError
from magiclinks.models import MagicLink
from magiclinks.settings import REGISTRATION_SALT
from magiclinks.utils import get_url_path

logger = logging.getLogger(__name__)
User = get_user_model()


def create_magiclink(*, email: str, domain: str, url_name: str, next_url: str, limit_seconds: int) -> str:
    """Create magiclink. Remove old magiclink is needed."""
    logger.info('Creating magiclink')
    # Set initial values
    email = email.lower()
    if not next_url:
        next_url = get_url_path(settings.LOGIN_REDIRECT_URL)

    # Check limit
    limit = timezone.now() - timedelta(seconds=limit_seconds)  # NOQA: E501
    if MagicLink.objects.filter(email=email, date_created__gte=limit).exists():
        raise MagicLinkError('Too many magic login requests')

    # Delete token for given E-mail if token exists
    delete_magiclink(email=email)

    # Register created token in the database
    magiclink = MagicLink(email=email)
    magiclink.save()

    # Sign token
    signed_token: str = signing.dumps(obj={'pk': str(magiclink.pk), 'email': email, 'next': next_url}, salt=REGISTRATION_SALT)

    return urljoin('https://{domain}'.format(domain=domain),
                   '{url_path}?{query}'.format(url_path=reverse(url_name), query=urlencode({'token': signed_token})))


def delete_magiclink(*, pk: Optional[Union[str, UUID]] = None, email: Optional[str] = None) -> None:
    """Delete magiclink."""
    logger.info('Deleting magiclink')
    if pk:
        MagicLink.objects.filter(pk=pk).delete()
    else:
        MagicLink.objects.filter(email=email).delete()


def send_magiclink(*, email: str, magiclink: str, subject: str,
                   email_templates: tuple[str, str] = ('magiclinks/login_email.txt', 'magiclinks/login_email.html')) -> None:
    """Send magiclink to E-mail."""
    logger.info('Sending magiclink')
    user: Optional[AbstractUser] = User.objects.filter(email=email, is_active=True).first()
    if not user:
        return

    context = {
        'subject': subject,
        'user': user,
        'magiclink': magiclink,
        'style': {
            'logo_url': '',
            'background_color': '#ffffff',
            'main_text_color': '#000000',
            'button_background_color': '#0078be',
            'button_text_color': '#ffffff',
        },
    }
    plain = render_to_string(email_templates[0], context)
    html = render_to_string(email_templates[1], context)
    send_mail(subject=subject, message=plain, recipient_list=[email], from_email=settings.DEFAULT_FROM_EMAIL, html_message=html)
