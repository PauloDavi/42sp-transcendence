from typing import ClassVar

from django import forms
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.users.models import User


class UserLoginForm(forms.Form):
    name = forms.CharField(
        label=_("Nome de login"),
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Ex: João Silva"),
            },
        ),
    )
    password = forms.CharField(
        label=_("Sua senha"),
        required=True,
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Digite sua senha"),
            },
        ),
    )

    def clean(self) -> dict:
        cleaned_data = super().clean()
        for field in self.errors:
            self.fields[field].widget.attrs["class"] += " is-invalid"
        return cleaned_data


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields: ClassVar[list[str]] = ["username", "email", "password1", "password2"]

        labels: ClassVar = {
            "username": _("Nome de usuário"),
            "email": _("E-mail"),
            "password1": _("Senha"),
            "password2": _("Confirme sua senha"),
        }

        widgets: ClassVar[dict[str, forms.Widget]] = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: João Silva")}),
            "email": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: joao@silva.com")}),
        }

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        for field_name, placeholder in {
            "password1": _("Crie uma senha"),
            "password2": _("Confirme sua senha"),
        }.items():
            self.fields[field_name].widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": placeholder,
                },
            )

    def clean(self) -> dict:
        cleaned_data = super().clean()
        for field in self.errors:
            self.fields[field].widget.attrs["class"] += " is-invalid"
        return cleaned_data


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields: ClassVar[list[str]] = ["email", "password"]


class UserEditProfileForm(BaseUserChangeForm):
    password = None
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "E-mail"}),
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )
    password1 = forms.CharField(
        required=False,
        max_length=50,
        label=_("Senha"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Senha")}),
    )
    password2 = forms.CharField(
        required=False,
        max_length=50,
        label=_("Confirme sua senha"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Confirme sua senha")}),
    )

    class Meta:
        model = User
        fields = ("email", "avatar", "password1", "password2")

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if (password1 or password2) and password1 != password2:
            raise forms.ValidationError(_("As senhas não coincidem."))
        return password2

    def save(self, commit: bool = True, request: HttpRequest | None = None) -> User:  # noqa: FBT002
        user = super().save(commit=False)

        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])

        if self.cleaned_data.get("avatar"):
            user.avatar = self.cleaned_data["avatar"]

        if commit:
            user.save()
            if request:
                update_session_auth_hash(request, user)

        return user

    def clean(self) -> dict:
        cleaned_data = super().clean()
        for field in self.errors:
            self.fields[field].widget.attrs["class"] += " is-invalid"
        return cleaned_data
