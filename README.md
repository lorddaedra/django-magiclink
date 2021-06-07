# Django MagicLinks


Passwordless Authentication for Django with Magic Links.

This package was created with a focus on ease of setup, security and testing. The idea is to use sane defaults to quickly create secure single-use token authentication for Django.

1. The user signs up via the sign up page
1. They enter their email on the login page to request a magic link
1. A magic link is sent to users email address
1. The user is redirected to a login sent page
1. The user clicks on the magic link in their email
1. The user is logged in and redirected

![](example.gif)


## Getting started

```bash
pip install django-magiclinks
```

The setup of the app is simple but has a few steps and a few templates that need overriding.

Add to the `urlpatterns` in `urls.py`:
```python
urlpatterns = [
    ...
    path('accounts/', include('magiclinks.urls', namespace='magiclinks')),
    ...
]
```

Add `magiclink` to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = (
    ...
    'magiclinks',
    ...
)
```

```python
AUTHENTICATION_BACKENDS = (
    'magiclinks.backends.MagicLinksBackend',
    ...
    'django.contrib.auth.backends.ModelBackend',
)
```
*Note: MagicLinksBackend should be placed at the top of AUTHENTICATION_BACKENDS* to ensure it is used as the primary login backend.


Check available settings in `magiclinks/settings.py` and configure them in your project `settings.py` module.
You may also set `LOGIN_REDIRECT_URL`, `LOGIN_URL` and `LOGOUT_REDIRECT_URL` options if any changes are needed.

Check available templates, copy to your `templates/magiclinks` directory and edit them as you need.
