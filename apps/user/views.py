from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings


class GoogleLoginView(SocialLoginView):
    """
    POST /api/v1/auth/google/
    Body: {"access_token": "<google_access_token>"}
         or {"code": "<auth_code>", "redirect_uri": "<frontend_callback_url>"}
    Returns: {"access": "...", "refresh": "..."}
    """
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = settings.GOOGLE_CALLBACK_URL


class FacebookLoginView(SocialLoginView):
    """
    POST /api/v1/auth/facebook/
    Body: {"access_token": "<facebook_access_token>"}
    Returns: {"access": "...", "refresh": "..."}
    """
    adapter_class = FacebookOAuth2Adapter


class GitHubLoginView(SocialLoginView):
    """
    POST /api/v1/auth/github/
    Body: {"code": "<auth_code>", "redirect_uri": "<frontend_callback_url>"}
    Returns: {"access": "...", "refresh": "..."}
    """
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client
    callback_url = settings.GITHUB_CALLBACK_URL
