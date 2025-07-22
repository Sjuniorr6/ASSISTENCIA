from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from clientes.models import Clientes
from orcamento.models import Orcamento
from rat.models import Rat


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home:index')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    # Estatísticas do sistema
    context = {
        'total_clientes': Clientes.objects.count(),
        'orcamentos_abertos': Orcamento.objects.filter(status='aberto').count(),
        'orcamentos_aprovados': Orcamento.objects.filter(status='aprovado').count(),
        'rats_pendentes': Rat.objects.filter(status='pendente').count(),
    }
    return render(request, 'accounts/profile.html', context) 