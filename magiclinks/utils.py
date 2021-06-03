from __future__ import annotations

from uuid import UUID

import timeflake
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch


def generate_timeflake() -> UUID:
    """Generate UUID for models uid fields."""
    return timeflake.random().uuid


def get_url_path(url: str) -> str:
    """
    url can either be a url name or a url path. First try and reverse a URL,
    if this does not exist then assume it's a url path
    """
    try:
        return reverse(url)
    except NoReverseMatch:
        return url
