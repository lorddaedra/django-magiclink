from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.http import HttpRequest
from django.urls import reverse

from magiclinks.models import MagicLink

from .fixtures import magic_link, user  # NOQA: F401

User = get_user_model()


@pytest.mark.django_db
def test_login_end_to_end(mocker, settings, client, user):  # NOQA: F811
    # spy = mocker.spy(services, 'create_magiclink')
    login_url = reverse('magiclinks:login')
    data = {'email': user.email}
    client.post(login_url, data, follow=True)
    # verify_url = spy.spy_return
    first_message = mail.outbox[0]
    verify_url = first_message.body.split('\n')[2]
    response = client.get(verify_url, follow=True)
    assert response.status_code == 200
    assert response.request['PATH_INFO'] == reverse('needs_login')

    url = reverse('magiclinks:logout')
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert response.request['PATH_INFO'] == reverse('no_login')

    url = reverse('needs_login')
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert response.request['PATH_INFO'] == reverse('magiclinks:login')


def test_login_page_get(client):
    url = reverse('magiclinks:login')
    response = client.get(url)
    assert response.context_data['login_form']
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_post(mocker, client, user, settings):  # NOQA: F811
    send_mail = mocker.patch('magiclinks.services.send_mail')

    url = reverse('magiclinks:login')
    data = {'email': user.email}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('magiclinks:login_sent')
    usr = User.objects.get(email=user.email)
    assert usr
    magiclink = MagicLink.objects.get(email=user.email)
    assert magiclink

    send_mail.assert_called_once_with(
        subject='Your login magic link',
        message=mocker.ANY,
        recipient_list=[user.email],
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=mocker.ANY,
    )


@pytest.mark.django_db
def test_login_post_no_user(client):
    url = reverse('magiclinks:login')
    data = {'email': 'fake@example.com'}
    response = client.post(url, data)
    assert response.status_code == 200
    error = ['We could not find a user with that email address']
    assert response.context_data['login_form'].errors['email'] == error


@pytest.mark.django_db
def test_login_email_ignore_case(settings, client, user):  # NOQA: F811
    url = reverse('magiclinks:login')
    data = {'email': user.email.upper()}
    response = client.post(url, data)
    magiclink = MagicLink.objects.get(email=user.email)
    assert magiclink
    assert response.status_code == 302
    assert response.url == reverse('magiclinks:login_sent')


@pytest.mark.django_db
def test_login_post_invalid(client, user):  # NOQA: F811
    url = reverse('magiclinks:login')
    data = {'email': 'notanemail'}
    response = client.post(url, data)
    assert response.status_code == 200
    error = ['Enter a valid email address.']
    assert response.context_data['login_form'].errors['email'] == error


@pytest.mark.django_db
def test_login_too_many_tokens(client, user, magic_link):  # NOQA: F811
    request = HttpRequest()
    magic_link(request)

    url = reverse('magiclinks:login')
    data = {'email': user.email}
    response = client.post(url, data)
    assert response.status_code == 200
    error = ['Too many magic login requests']
    assert response.context_data['login_form'].errors['email'] == error


@pytest.mark.django_db
def test_login_not_active(settings, client, user):  # NOQA: F811
    user.is_active = False
    user.save()

    url = reverse('magiclinks:login')
    data = {'email': user.email}

    response = client.post(url, data)
    assert response.status_code == 200
    error = ['This user has been deactivated']
    assert response.context_data['login_form'].errors['email'] == error
