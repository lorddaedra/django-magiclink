from __future__ import annotations

from uuid import UUID

from magiclinks.utils import generate_timeflake, get_url_path


def test_generate_timeflake():
    assert isinstance(generate_timeflake(), UUID)
    assert generate_timeflake() != generate_timeflake()


def test_get_url_path_with_name():
    url_name = 'no_login'
    url = get_url_path(url_name)
    assert url == '/no-login/'


def test_get_url_path_with_path():
    url_name = '/test/'
    url = get_url_path(url_name)
    assert url == '/test/'
