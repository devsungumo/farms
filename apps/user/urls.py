from django.urls import path
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView
from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
    UserDetailsView,
)
from rest_framework_simplejwt.views import TokenRefreshView

from .views import FacebookLoginView, GitHubLoginView, GoogleLoginView

urlpatterns = [
    # Email / password
    path('signup/',          RegisterView.as_view(),              name='auth-signup'),
    path('verify-email/',    VerifyEmailView.as_view(),           name='auth-verify-email'),
    path('login/',           LoginView.as_view(),                 name='auth-login'),
    path('logout/',          LogoutView.as_view(),                name='auth-logout'),
    path('token/refresh/',   TokenRefreshView.as_view(),          name='token-refresh'),
    path('me/',              UserDetailsView.as_view(),           name='auth-user'),
    path('password/change/', PasswordChangeView.as_view(),       name='password-change'),
    path('password/reset/',  PasswordResetView.as_view(),        name='password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # Social auth
    path('google/',   GoogleLoginView.as_view(),   name='auth-google'),
    path('facebook/', FacebookLoginView.as_view(), name='auth-facebook'),
    path('github/',   GitHubLoginView.as_view(),   name='auth-github'),
]
