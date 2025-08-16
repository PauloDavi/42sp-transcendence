from typing import ClassVar

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.matchmaking.models import Tournament


class CreateTournament(forms.ModelForm):
    display_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Digite seu nome de exibição"),
            },
        ),
        label=_("Seu nome de exibição"),
    )

    class Meta:
        model = Tournament
        fields: ClassVar[list[str]] = ["name"]
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Ex: Torneio 42"),
                },
            ),
        }


class JoinTournament(forms.Form):
    display_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Digite seu nome de exibição"),
            },
        ),
        label=_("Seu nome de exibição"),
    )
