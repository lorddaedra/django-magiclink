from __future__ import annotations

from django.urls import path

from .views import LoginSentView, LoginVerifyView, LoginView, LogoutView, SignupView

app_name = "magiclink"

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login/sent/', LoginSentView.as_view(), name='login_sent'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/verify/', LoginVerifyView.as_view(), name='login_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
