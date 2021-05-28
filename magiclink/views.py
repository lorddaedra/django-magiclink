import logging

from django.conf import settings as django_settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from . import settings
from .forms import LoginForm, SignupForm
from .helpers import create_magiclink, get_or_create_user
from .models import MagicLink, MagicLinkError
from .utils import get_url_path

User = get_user_model()
log = logging.getLogger(__name__)


class Login(TemplateView):
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
        context['login_form'] = LoginForm()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        logout(request)
        context = self.get_context_data(**kwargs)
        form = LoginForm(request.POST)
        if not form.is_valid():
            context['login_form'] = form
            return self.render_to_response(context)

        email = form.cleaned_data['email']

        next_url = request.GET.get('next', '')
        try:
            magiclink = create_magiclink(email, request, redirect_url=next_url)
        except MagicLinkError as e:
            form.add_error('email', str(e))
            context['login_form'] = form
            return self.render_to_response(context)

        MagicLink.send(magiclink, request, style=self.style)

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
                MagicLink.validate(magiclink, email)
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
        full_name = form.cleaned_data.get('name', '')
        try:
            first_name, last_name = full_name.split(' ', 1)
        except ValueError:
            first_name = full_name
            last_name = ''

        get_or_create_user(
            email=email,
            username=form.cleaned_data.get('username', ''),
            first_name=first_name,
            last_name=last_name
        )
        default_signup_redirect = get_url_path(settings.SIGNUP_LOGIN_REDIRECT)
        next_url = request.GET.get('next', default_signup_redirect)
        magiclink = create_magiclink(email, request, redirect_url=next_url)
        MagicLink.send(magiclink, request, style=self.style)

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
