from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django_registration.validators import HTML5EmailValidator, validate_confusables_email

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': 'autofocus', 'placeholder': 'Enter your email'}))

    def clean_email(self) -> str:
        email = self.cleaned_data['email'].lower()
        HTML5EmailValidator()(email)
        validate_confusables_email(email)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            error = 'We could not find a user with that email address'
            raise forms.ValidationError(error)
        else:
            if not user.is_active:
                raise forms.ValidationError('This user has been deactivated')

        return email


class SignupForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': 'autofocus', 'placeholder': 'Enter your email'}))

    def clean_email(self) -> str:
        email = self.cleaned_data['email'].lower()
        HTML5EmailValidator()(email)
        validate_confusables_email(email)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        else:
            error = 'Email address is already linked to an account'
            if not user.is_active:
                error = 'This user has been deactivated'
            raise forms.ValidationError(error)
