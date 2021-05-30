from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView

from . import settings as ml_settings
from .forms import LoginForm, SignupForm
from .models import MagicLink, MagicLinkError
from .services import create_magiclink, create_user, send_magiclink, validate_magiclink
from .utils import get_client_ip, get_url_path

User = get_user_model()
logger = logging.getLogger(__name__)


@method_decorator((user_passes_test(lambda u: not u.is_authenticated, login_url='/'), sensitive_post_parameters(), csrf_protect, never_cache), name='dispatch')
class LoginView(TemplateView):
    form = LoginForm
    limit_seconds = 3
    expiry_seconds = 900
    subject: str = 'Your login magic link'
    template_name: str = 'magiclink/login.html'
    style: dict[str, str] = {
        'logo_url': '',
        'background_color': '#ffffff',
        'main_text_color': '#000000',
        'button_background_color': '#0078be',
        'button_text_color': '#ffffff',
    }
    next_page: str = ml_settings.LOGIN_SENT_REDIRECT

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
            magiclink = create_magiclink(email=email, ip_address=get_client_ip(request), redirect_url=next_url,
                                         limit_seconds=self.limit_seconds, expiry_seconds=self.expiry_seconds)
        except MagicLinkError as e:
            form.add_error('email', str(e))
            context['login_form'] = form
            return self.render_to_response(context)

        send_magiclink(ml=magiclink, domain=str(get_current_site(request).domain), subject=self.subject, style=self.style)

        success_url: str = get_url_path(self.next_page)

        if request.META.get("HTTP_HX_REQUEST") != 'true':
            return HttpResponseRedirect(success_url)

        # htmx request
        response: HttpResponse = HttpResponse()
        response.headers['HX-Redirect'] = success_url
        return response


class LoginSentView(TemplateView):
    template_name: str = 'magiclink/login_sent.html'


@method_decorator((user_passes_test(lambda u: not u.is_authenticated, login_url='/'), never_cache), name='dispatch')
class LoginVerifyView(TemplateView):
    template_name: str = 'magiclink/login_failed.html'

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token', '')
        email = request.GET.get('email', '')
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
        logger.info(f'Login successful for {email}')

        magiclink = MagicLink.objects.get(token=token)

        return HttpResponseRedirect(magiclink.redirect_url)


@method_decorator((user_passes_test(lambda u: not u.is_authenticated, login_url='/'), sensitive_post_parameters(), csrf_protect, never_cache), name='dispatch')
class SignupView(TemplateView):
    form = SignupForm
    limit_seconds = 3
    expiry_seconds = 900
    subject = 'Your login magic link'
    template_name: str = 'magiclink/signup.html'
    style: dict[str, str] = {
        'logo_url': '',
        'background_color': '#ffffff',
        'main_text_color': '#000000',
        'button_background_color': '#0078be',
        'button_text_color': '#ffffff',
    }
    next_page: str = ml_settings.LOGIN_SENT_REDIRECT

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

        create_user(email=email)

        redirect_to: str = request.POST.get('next', request.GET.get('next', ''))
        url_is_safe: bool = url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()}, require_https=True)
        next_url: str = redirect_to if url_is_safe else get_url_path(ml_settings.SIGNUP_LOGIN_REDIRECT)

        magiclink = create_magiclink(email=email, ip_address=get_client_ip(request), redirect_url=next_url,
                                     limit_seconds=self.limit_seconds, expiry_seconds=self.expiry_seconds)
        send_magiclink(ml=magiclink, domain=str(get_current_site(request).domain), subject=self.subject, style=self.style)

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
