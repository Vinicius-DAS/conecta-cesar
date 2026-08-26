from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login
from rolepermissions.checkers import has_role
from project_cc.roles import Aluno, Professor
from app_cc.models import Aluno as AlunoModel
from app_cc.forms import CadastroForm
from django.contrib import messages
from rolepermissions.roles import assign_role
from django.utils.translation import gettext as _





# Cadastro de novo usuário
def cadastro(request):
    """
    View function for user registration.

    Public self-registration only ever creates an aluno account — there's
    no approval step here, so letting visitors pick 'professor' themselves
    would hand out grade/attendance-management access to anyone. Professor
    accounts are created via Django Admin by an existing staff member.
    """

    # The only way for the request to be a GET is if the user tries to access the registration page directly by typing the URL in the browser.
    # In this case, we simply render the registration form.
    if request.method == 'GET':
        return render(request, 'cadastro.html')

    else:
        form = CadastroForm(request.POST)
        if not form.is_valid():
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
            return redirect("cadastro")

        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['senha'],
        )
        assign_role(user, Aluno)
        AlunoModel.objects.create(usuario=user, email=form.cleaned_data['email'])

        # Success message
        messages.success(request, _("Usuário cadastrado com sucesso. Agora faça login."))
        return redirect("login")  # Redirect to the login page

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        user_name = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=user_name, password=senha)
        if user:
            # A função django-login é necessária para que o usuário seja considerado logado no sistema.
            # A biblioteca Django mantém o estado do usuário logado usando um cookie.
            # A função django-login cria e atualiza esse cookie para que o usuário seja considerado logado.
            django_login(request, user)
            
            if has_role(user, Professor):
                return redirect("avisosp")  # URL da página do professor
            
            elif has_role(user, Aluno):
                return redirect("avisos")  # URL da página do aluno
            else:
                messages.error(request, _("O usuário não tem um papel definido."))
                return redirect("login")  # Volta para a página de login
        else:
            messages.error(request, _("Usuário ou senha incorretos. Por favor, tente novamente."))
            return redirect("login")  # Redireciona para a página de login

def plataforma(request):
    if request.user.is_authenticated:  
        if has_role(request.user, Professor):
            return redirect("avisosp")  # Redireciona para a página do professor
        elif has_role(request.user, Aluno):
            return redirect("avisos")  # Redireciona para a página do aluno
    return HttpResponse(_('Você precisa estar logado'))
