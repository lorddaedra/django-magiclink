from __future__ import annotations

import logging
from importlib import import_module
from urllib.parse import unquote_plus

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView

from .exceptions import MagicLinkError
from .forms import LoginForm, SignupForm
from .services import create_magiclink, send_magiclink
from .settings import CREATE_USER_CALLABLE, LOGIN_SENT_REDIRECT_URL, REGISTRATION_SALT, SIGNUP_LOGIN_REDIRECT_URL
from .utils import get_url_path

User = get_user_model()
logger = logging.getLogger(__name__)


@method_decorator((user_passes_test(lambda u: not u.is_authenticated, login_url='/'), sensitive_post_parameters(), csrf_protect, never_cache), name='dispatch')
class LoginView(TemplateView):
    form = LoginForm
    limit_seconds: int = 3
    subject: str = 'Your login magic link'
    template_name: str = 'magiclinks/login.html'
    login_verify_url_name: str = 'magiclinks:login_verify'
    email_templates: tuple[str, str] = ('magiclinks/login_email.txt', 'magiclinks/login_email.html')
    style: dict[str, str] = {
        'logo_url': '',
        'background_color': '#ffffff',
        'main_text_color': '#000000',
        'button_background_color': '#0078be',
        'button_text_color': '#ffffff',
    }
    next_page: str = LOGIN_SENT_REDIRECT_URL

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['login_form'] = self.form()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = self.form(request.POST)
        if not form.is_valid():
            context['login_form'] = form
            return self.render_to_response(context)

        email = form.cleaned_data['email']

        redirect_to: str = request.POST.get('next', request.GET.get('next', ''))
        url_is_safe: bool = url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()}, require_https=True)
        next_url: str = redirect_to if url_is_safe else get_url_path(settings.LOGIN_REDIRECT_URL)

        try:
            magiclink = create_magiclink(email=email, domain=str(get_current_site(request).domain), url_name=self.login_verify_url_name, next_url=next_url,
                                         limit_seconds=self.limit_seconds)
        except MagicLinkError as e:
            form.add_error('email', str(e))
            context['login_form'] = form
            return self.render_to_response(context)

        send_magiclink(email=email, magiclink=magiclink, subject=self.subject, email_templates=self.email_templates, style=self.style)

        success_url: str = get_url_path(self.next_page)

        if request.META.get("HTTP_HX_REQUEST") != 'true':
            return HttpResponseRedirect(success_url)

        # htmx request
        response: HttpResponse = HttpResponse()
        response.headers['HX-Redirect'] = success_url
        return response


class LoginSentView(TemplateView):
    template_name: str = 'magiclinks/login_sent.html'


@method_decorator((user_passes_test(lambda u: not u.is_authenticated, login_url='/'), never_cache), name='dispatch')
class LoginVerifyView(View):
    expiry_seconds: int = 900
    error_message: str = 'Token is invalid or expired. Please, try again.'

    def get(self, request, *args, **kwargs):
        signed_token: str = request.GET.get('token', '')
        if not signed_token:
            messages.error(request, self.error_message, fail_silently=True)
            return HttpResponseRedirect(get_url_path(settings.LOGIN_URL))

        signed_token = unquote_plus(signed_token)
        user = authenticate(request, token=signed_token, expiry_seconds=self.expiry_seconds)
        if not user:
            messages.error(request, self.error_message, fail_silently=True)
            return HttpResponseRedirect(get_url_path(settings.LOGIN_URL))

        login(request, user)
        logger.info(f'Login successful for {user}')

        next_url: str = signing.loads(signed_token, salt=REGISTRATION_SALT)['next']

        return HttpResponseRedirect(next_url)


@method_decorator((user_passes_test(lambda u: not u.is_authenticated, login_url='/'), sensitive_post_parameters(), csrf_protect, never_cache), name='dispatch')
class SignupView(TemplateView):
    form = SignupForm
    limit_seconds: int = 3
    subject: str = 'Your login magic link'
    template_name: str = 'magiclinks/signup.html'
    login_verify_url_name: str = 'magiclinks:login_verify'
    email_templates: tuple[str, str] = ('magiclinks/login_email.txt', 'magiclinks/login_email.html')
    style: dict[str, str] = {
        'logo_url': '',
        'background_color': '#ffffff',
        'main_text_color': '#000000',
        'button_background_color': '#0078be',
        'button_text_color': '#ffffff',
    }
    next_page: str = LOGIN_SENT_REDIRECT_URL

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['signup_form'] = self.form()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        form = self.form(request.POST)
        if not form.is_valid():
            context['signup_form'] = form
            return self.render_to_response(context)

        email = form.cleaned_data['email']

        module_name, callable_name = CREATE_USER_CALLABLE.split(':')
        getattr(import_module(module_name), callable_name)(email=email)

        redirect_to: str = request.POST.get('next', request.GET.get('next', ''))
        url_is_safe: bool = url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()}, require_https=True)
        next_url: str = redirect_to if url_is_safe else get_url_path(SIGNUP_LOGIN_REDIRECT_URL)

        magiclink = create_magiclink(email=email, domain=str(get_current_site(request).domain), url_name=self.login_verify_url_name, next_url=next_url,
                                     limit_seconds=self.limit_seconds)
        send_magiclink(email=email, magiclink=magiclink, subject=self.subject, email_templates=self.email_templates, style=self.style)

        success_url: str = get_url_path(self.next_page)

        if request.META.get("HTTP_HX_REQUEST") != 'true':
            return HttpResponseRedirect(success_url)

        # htmx request
        response: HttpResponse = HttpResponse()
        response.headers['HX-Redirect'] = success_url
        return response


class LogoutView(View):
    """
    Log out the user.
    """
    next_page: str = settings.LOGOUT_REDIRECT_URL

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        logout(request)

        redirect_to: str = request.POST.get('next', request.GET.get('next', ''))
        url_is_safe: bool = url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()}, require_https=True)
        next_url: str = redirect_to if url_is_safe else get_url_path(self.next_page)

        if request.META.get("HTTP_HX_REQUEST") != 'true':
            return HttpResponseRedirect(next_url)

        # htmx request
        response: HttpResponse = HttpResponse()
        response.headers['HX-Redirect'] = next_url
        return response
