from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from apps.users.models import User
from django.utils.translation import gettext as _

class UserLoginForm(forms.Form):
    name = forms.CharField(
        label=_("Nome de login"),
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Ex: João Silva"),
            }
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
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        for field in self.errors:
            self.fields[field].widget.attrs["class"] += " is-invalid"
        return cleaned_data

class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        
        labels = {
            "username": _("Nome de usuário"),
            "email": _("E-mail"),
            "password1": _("Senha"),
            "password2": _("Confirme sua senha"),
        }
        
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: João Silva")}),
            "email": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: joao@silva.com")}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, placeholder in {"password1": _("Crie uma senha"), "password2": _("Confirme sua senha")}.items():
            self.fields[field_name].widget.attrs.update({
                "class": "form-control",
                "placeholder": placeholder,
            })

    def clean(self):
        cleaned_data = super().clean()
        for field in self.errors:
            self.fields[field].widget.attrs["class"] += " is-invalid"
        return cleaned_data

class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "password"]

class UserEditProfileForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}),
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )
    password1 = forms.CharField(
        required=False,
        max_length=50,
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Senha')}),
    )
    password2 = forms.CharField(
        required=False,
        max_length=50,
        label='Confirme sua senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirme sua senha')}),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("As senhas não coincidem."))
        return password2

    def save(self, user, commit=True):
        user.email = self.cleaned_data['email']
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
        if 'avatar' in self.cleaned_data and self.cleaned_data['avatar']:
            user.avatar = self.cleaned_data['avatar']
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        for field in self.errors:
            self.fields[field].widget.attrs["class"] += " is-invalid"
        return cleaned_data

class ChatForm(forms.Form):
    content = forms.CharField(
        label=_("Sua mensagem"),
        required=True
    )
