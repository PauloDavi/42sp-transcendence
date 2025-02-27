from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class FortyTwoOAuth2Adapter(OAuth2Adapter):
    provider_id = "fortytwo"
    settings = app_settings.PROVIDERS.get(provider_id, {})

    web_url = "https://api.intra.42.fr"
    access_token_url = f"{web_url}/oauth/token"
    authorize_url = f"{web_url}/oauth/authorize"
    profile_url = f"{web_url}/v2/me"

    def get_callback_url(self, request: any, app: any) -> str:
        base_url = super().get_callback_url(request, app)
        return base_url.removesuffix("/")

    def complete_login(self, request: any, app: any, token: SocialToken, **kwargs: dict) -> any:
        headers = {"Authorization": f"Bearer {token.token}"}
        resp = get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FortyTwoOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FortyTwoOAuth2Adapter)
