from datetime import timedelta
import pytest
from django.http import HttpRequest
from django.utils import timezone

from magiclink.backends import MagicLinkBackend
from magiclink import settings

from .fixtures import user, magic_link  # NOQA: F401


@pytest.mark.django_db
def test_auth_backend_get_user(user):  # NOQA: F811
    assert MagicLinkBackend().get_user(user.id)


@pytest.mark.django_db
def test_auth_backend_get_user_do_not_exist(user):  # NOQA: F811
    assert MagicLinkBackend().get_user(123456) is None


@pytest.mark.django_db
def test_auth_backend(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    request.COOKIES['magiclink'] = ml.cookie_value
    user = MagicLinkBackend().authenticate(
        request=request, token=ml.token, email=user.email
    )
    assert user


@pytest.mark.django_db
def test_auth_backend_email_ignore_case(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    request.COOKIES['magiclink'] = ml.cookie_value
    user = MagicLinkBackend().authenticate(
        request=request, token=ml.token, email=user.email.upper()
    )
    assert user


@pytest.mark.django_db
def test_auth_backend_no_token(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    user = MagicLinkBackend().authenticate(
        request=request, token='fake', email=user.email
    )
    assert user is None


@pytest.mark.django_db
def test_auth_backend_disabled_token(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    request.COOKIES['magiclink'] = ml.cookie_value
    ml.disabled = True
    ml.save()
    user = MagicLinkBackend().authenticate(
        request=request, token=ml.token, email=user.email
    )
    assert user is None


@pytest.mark.django_db
def test_auth_backend_no_email(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    request.COOKIES['magiclink'] = ml.cookie_value
    user = MagicLinkBackend().authenticate(request=request, token=ml.token)
    assert user is None


@pytest.mark.django_db
def test_auth_backend_wrong_email(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    request.COOKIES['magiclink'] = ml.cookie_value
    user = MagicLinkBackend().authenticate(
        request=request, token=ml.token, email='fake@email.com'
    )
    assert user is None


@pytest.mark.django_db
def test_auth_backend_expired(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    request.COOKIES['magiclink'] = ml.cookie_value
    ml.expiry = timezone.now() - timedelta(seconds=1)
    ml.save()
    user = MagicLinkBackend().authenticate(
        request=request, token=ml.token, email=user.email
    )
    assert user is None


@pytest.mark.django_db
def test_auth_backend_wrong_ip(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    request.COOKIES['magiclink'] = ml.cookie_value
    ml.ip_address = '255.255.255.255'
    ml.save()
    user = MagicLinkBackend().authenticate(
        request=request, token=ml.token, email=user.email
    )
    assert user is None


@pytest.mark.django_db
def test_auth_backend_different_browser(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    request.COOKIES['magiclink'] = 'bad_value'
    user = MagicLinkBackend().authenticate(
        request=request, token=ml.token, email=user.email
    )
    assert user is None


@pytest.mark.django_db
def test_auth_backend_used_times(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    request.COOKIES['magiclink'] = ml.cookie_value
    ml.times_used = settings.TOKEN_USES
    ml.save()
    user = MagicLinkBackend().authenticate(
        request=request, token=ml.token, email=user.email
    )
    assert user is None


@pytest.mark.django_db
def test_auth_backend_superuser(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    request.COOKIES['magiclink'] = ml.cookie_value
    user.is_superuser = True
    user.save()
    user = MagicLinkBackend().authenticate(
        request=request, token=ml.token, email=user.email
    )
    assert user is None


@pytest.mark.django_db
def test_auth_backend_staff(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    request.COOKIES['magiclink'] = ml.cookie_value
    user.is_staff = True
    user.save()
    user = MagicLinkBackend().authenticate(
        request=request, token=ml.token, email=user.email
    )
    assert user is None
