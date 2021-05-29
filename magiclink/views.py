from __future__ import annotations

import logging

from django.conf import settings as django_settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from . import settings
from .forms import LoginForm, SignupForm
from .models import MagicLink, MagicLinkError
from .services import create_magiclink, create_user, send_magiclink, validate_magiclink
from .utils import get_client_ip, get_url_path

User = get_user_model()
log = logging.getLogger(__name__)


class Login(TemplateView):
    form = LoginForm
    subject: str = 'Your login magic link'
    template_name: str = 'magiclink/login.html'
    style: dict[str, str] = {
        'logo_url': '',
        'background_color': '#ffffff',
        'main_text_color': '#000000',
        'button_background_color': '#0078be',
        'button_text_color': '#ffffff',
    }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['login_form'] = self.form()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        logout(request)
        context = self.get_context_data(**kwargs)
        form = self.form(request.POST)
        if not form.is_valid():
            context['login_form'] = form
            return self.render_to_response(context)

        email = form.cleaned_data['email']

        next_url = request.GET.get('next', '')
        try:
            magiclink = create_magiclink(email=email, ip_address=get_client_ip(request), redirect_url=next_url)
        except MagicLinkError as e:
            form.add_error('email', str(e))
            context['login_form'] = form
            return self.render_to_response(context)

        send_magiclink(ml=magiclink, domain=str(get_current_site(request).domain), subject=self.subject, style=self.style)

        sent_url = get_url_path(settings.LOGIN_SENT_REDIRECT)
        response = HttpResponseRedirect(sent_url)
        return response


class LoginSent(TemplateView):
    template_name: str = 'magiclink/login_sent.html'


class LoginVerify(TemplateView):
    template_name: str = 'magiclink/login_failed.html'

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        email = request.GET.get('email')
        user = authenticate(request, token=token, email=email)
        if not user:
            context = self.get_context_data(**kwargs)

            try:
                magiclink = MagicLink.objects.get(token=token)
            except MagicLink.DoesNotExist:
                error = 'A magic link with that token could not be found'
                context['login_error'] = error
                return self.render_to_response(context)

            try:
                validate_magiclink(ml=magiclink, email=email)
            except MagicLinkError as error:
                context['login_error'] = str(error)

            return self.render_to_response(context)

        login(request, user)
        log.info(f'Login successful for {email}')

        magiclink = MagicLink.objects.get(token=token)
        response = HttpResponseRedirect(magiclink.redirect_url)
        return response


class Signup(TemplateView):
    form = SignupForm
    subject = 'Your login magic link'
    template_name: str = 'magiclink/signup.html'
    style: dict[str, str] = {
        'logo_url': '',
        'background_color': '#ffffff',
        'main_text_color': '#000000',
        'button_background_color': '#0078be',
        'button_text_color': '#ffffff',
    }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['signup_form'] = self.form()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        logout(request)
        context = self.get_context_data(**kwargs)

        form = self.form(request.POST)
        if not form.is_valid():
            context['signup_form'] = form
            return self.render_to_response(context)

        email = form.cleaned_data['email']

        create_user(email=email)
        default_signup_redirect = get_url_path(settings.SIGNUP_LOGIN_REDIRECT)
        next_url = request.GET.get('next', default_signup_redirect)
        magiclink = create_magiclink(email=email, ip_address=get_client_ip(request), redirect_url=next_url)
        send_magiclink(ml=magiclink, domain=str(get_current_site(request).domain), subject=self.subject, style=self.style)

        sent_url = get_url_path(settings.LOGIN_SENT_REDIRECT)
        response = HttpResponseRedirect(sent_url)
        return response


class Logout(RedirectView):

    def get(self, request, *args, **kwargs):
        logout(self.request)

        next_page = request.GET.get('next')
        if next_page:
            return HttpResponseRedirect(next_page)

        redirect_url = get_url_path(django_settings.LOGOUT_REDIRECT_URL)
        return HttpResponseRedirect(redirect_url)
