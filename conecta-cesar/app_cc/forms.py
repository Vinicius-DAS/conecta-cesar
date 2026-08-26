from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CadastroForm(forms.Form):
    """Public self-registration form — always creates an aluno account.
    Professor accounts are created via Django Admin by existing staff."""

    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    senha = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError(_("Já existe um usuário com esse nome"))
        return username

    def clean_senha(self):
        senha = self.cleaned_data["senha"]
        try:
            validate_password(senha)
        except ValidationError as error:
            raise ValidationError(error.messages) from error
        return senha
