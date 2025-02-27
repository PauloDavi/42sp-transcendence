from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

from apps.users.providers.fortytwo.views import FortyTwoOAuth2Adapter


class FortyTwoAccount(ProviderAccount):
    def get_profile_url(self) -> str | None:
        return self.account.extra_data.get("url")

    def get_avatar_url(self) -> str | None:
        return self.account.extra_data.get("image_url")


class FortyTwoProvider(OAuth2Provider):
    id = "fortytwo"
    name = "42 School"
    account_class = FortyTwoAccount
    oauth2_adapter_class = FortyTwoOAuth2Adapter

    def get_default_scope(self) -> list[str]:
        return ["public"]

    def extract_uid(self, data: dict) -> str:
        return str(data["id"])

    def extract_common_fields(self, data: dict) -> dict:
        return {
            "email": data.get("email"),
            "username": data.get("login"),
            "name": data.get("displayname"),
        }

    def extract_extra_data(self, data: dict) -> dict:
        data["avatar_url"] = data.get("image", {}).get("link", "")
        return data

    def extract_email_addresses(self, data: dict) -> list[EmailAddress]:
        ret = []
        if "email" in data:
            ret.append(EmailAddress(email=data["email"], primary=True, verified=True))
        return ret


provider_classes = [FortyTwoProvider]
