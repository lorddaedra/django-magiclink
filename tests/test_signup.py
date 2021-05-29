from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from magiclink import services
from magiclink.models import MagicLink

User = get_user_model()


@pytest.mark.django_db
def test_signup_end_to_end(mocker, settings, client):
    from magiclink import settings as mlsettings
    spy = mocker.spy(services, 'generate_url')

    login_url = reverse('magiclink:signup')
    email = 'test@example.com'
    data = {
        'email': email,
    }
    client.post(login_url, data, follow=True)
    verify_url = spy.spy_return
    response = client.get(verify_url, follow=True)
    assert response.status_code == 200
    signup_redirect_page = reverse(mlsettings.SIGNUP_LOGIN_REDIRECT)
    assert response.request['PATH_INFO'] == signup_redirect_page
    User.objects.get(email=email)

    url = reverse('magiclink:logout')
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert response.request['PATH_INFO'] == reverse('no_login')

    url = reverse('needs_login')
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert response.request['PATH_INFO'] == reverse('magiclink:login')


def test_signup_get(client):
    url = reverse('magiclink:signup')
    response = client.get(url)
    assert response.context_data['signup_form']
    assert response.status_code == 200


@pytest.mark.django_db
def test_signup_post(mocker, client, settings):  # NOQA: F811
    send_mail = mocker.patch('magiclink.services.send_mail')

    url = reverse('magiclink:signup')
    email = 'test@example.com'
    data = {
        'email': email,
        'name': 'testname',
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('magiclink:login_sent')

    usr = User.objects.get(email=email)
    assert usr
    magiclink = MagicLink.objects.get(email=email)
    assert magiclink

    send_mail.assert_called_once_with(
        subject='Your login magic link',
        message=mocker.ANY,
        recipient_list=[email],
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=mocker.ANY,
    )


@pytest.mark.django_db
def test_signup_form_user_exists(mocker, client):
    email = 'test@example.com'
    User.objects.create(email=email)
    url = reverse('magiclink:signup')

    data = {
        'email': email,
    }
    response = client.post(url, data)
    assert response.status_code == 200
    error = ['Email address is already linked to an account']
    response.context_data['signup_form'].errors['email'] == error


@pytest.mark.django_db
def test_signup_form_user_exists_inactive(mocker, client):
    email = 'test@example.com'
    User.objects.create(email=email, is_active=False)
    url = reverse('magiclink:signup')

    data = {
        'email': email,
    }
    response = client.post(url, data)
    assert response.status_code == 200
    error = ['This user has been deactivated']
    response.context_data['signup_form'].errors['email'] == error


@pytest.mark.django_db
def test_signup_form_email_only(mocker, client):
    url = reverse('magiclink:signup')
    email = 'test@example.com'
    data = {
        'email': email,
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('magiclink:login_sent')
