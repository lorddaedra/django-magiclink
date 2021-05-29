from importlib import reload
from time import time

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from magiclink.models import MagicLink

User = get_user_model()


@pytest.mark.django_db
def test_signup_end_to_end(mocker, settings, client):
    from magiclink import settings as mlsettings
    spy = mocker.spy(MagicLink, 'generate_url')

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
    from magiclink import settings as mlsettings
    send_mail = mocker.patch('magiclink.models.send_mail')

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
        subject=mlsettings.EMAIL_SUBJECT,
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


@pytest.mark.django_db
def test_signup_antispam(settings, client, freezer):  # NOQA: F811
    freezer.move_to('2000-01-01T00:00:00')

    submit_time = 1
    settings.MAGICLINK_ANTISPAM_FORMS = True
    settings.MAGICLINK_ANTISPAM_FIELD_TIME = submit_time
    from magiclink import settings as mlsettings
    reload(mlsettings)

    url = reverse('magiclink:signup')
    email = 'test@example.com'
    data = {
        'email': email,
        'username': 'uname',
        'name': 'Fake name',
        'load_time': time() - (submit_time * 3),
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('magiclink:login_sent')


@pytest.mark.django_db
def test_signup_antispam_submit_too_fast(settings, client, freezer):  # NOQA: F811,E501
    freezer.move_to('2000-01-01T00:00:00')

    settings.MAGICLINK_ANTISPAM_FORMS = True
    from magiclink import settings as mlsettings
    reload(mlsettings)

    url = reverse('magiclink:signup')
    data = {
        'email': 'test@example.com',
        'load_time': time()
    }

    response = client.post(url, data)
    assert response.status_code == 200
    form_errors = response.context['signup_form'].errors
    assert form_errors['load_time'] == ['Form filled out too fast - bot detected']  # NOQA: E501


@pytest.mark.django_db
def test_signup_antispam_missing_load_time(settings, client):  # NOQA: F811
    settings.MAGICLINK_ANTISPAM_FORMS = True
    from magiclink import settings as mlsettings
    reload(mlsettings)

    url = reverse('magiclink:signup')
    data = {'email': 'test@example.com'}

    response = client.post(url, data)
    assert response.status_code == 200
    form_errors = response.context['signup_form'].errors
    assert form_errors['load_time'] == ['This field is required.']


@pytest.mark.django_db
def test_signup_antispam_invalid_load_time(settings, client):  # NOQA: F811
    settings.MAGICLINK_ANTISPAM_FORMS = True
    from magiclink import settings as mlsettings
    reload(mlsettings)

    url = reverse('magiclink:signup')
    data = {
        'email': 'test@example.com',
        'load_time': 'test'
    }

    response = client.post(url, data)
    assert response.status_code == 200
    form_errors = response.context['signup_form'].errors
    assert form_errors['load_time'] == ['Invalid value']


@pytest.mark.django_db
def test_signup_antispam_url_value(settings, client):  # NOQA: F811
    settings.MAGICLINK_ANTISPAM_FORMS = True
    from magiclink import settings as mlsettings
    reload(mlsettings)

    url = reverse('magiclink:signup')
    data = {
        'email': 'test@example.com',
        'url': 'test',
    }
    response = client.post(url, data)
    assert response.status_code == 200
    form_errors = response.context['signup_form'].errors
    assert form_errors['url'] == ['url should be empty']
