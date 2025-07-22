from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from .models import AgendaDia, Visita
from .forms import VisitaForm
from datetime import timedelta, date

# Create your views here.

# Página principal da agenda

def agenda_home(request):
    hoje = timezone.localdate()
    # Navegação por querystring
    data_str = request.GET.get('data')
    if data_str:
        dia_base = date.fromisoformat(data_str)
    else:
        dia_base = hoje
    anterior = (dia_base - timedelta(days=1)).isoformat()
    proximo = (dia_base + timedelta(days=1)).isoformat()
    agenda_hoje, _ = AgendaDia.objects.get_or_create(data=dia_base, defaults={'dia_semana': dia_base.strftime('%A')})
    proximos_dias = [dia_base + timedelta(days=i) for i in range(1, 5)]
    agendas = [AgendaDia.objects.get_or_create(data=d, defaults={'dia_semana': d.strftime('%A')})[0] for d in proximos_dias]
    return render(request, 'agenda/agenda.html', {
        'agenda_hoje': agenda_hoje,
        'agendas': agendas,
        'hoje': dia_base,
        'anterior': anterior,
        'proximo': proximo,
        'active_tab': 'agenda',
    })

# Visualizar um dia específico

def agenda_dia(request, data):
    data_obj = date.fromisoformat(data)
    agenda = get_object_or_404(AgendaDia, data=data_obj)
    # Navegação
    anterior = (data_obj - timedelta(days=1)).isoformat()
    proximo = (data_obj + timedelta(days=1)).isoformat()
    return render(request, 'agenda/agenda_dia.html', {
        'agenda': agenda,
        'anterior': anterior,
        'proximo': proximo,
        'active_tab': 'agenda',
    })

# Agendar nova visita

def agendar_visita(request):
    if request.method == 'POST':
        form = VisitaForm(request.POST)
        if form.is_valid():
            data = request.POST.get('data')
            agenda, _ = AgendaDia.objects.get_or_create(data=data, defaults={'dia_semana': date.fromisoformat(data).strftime('%A')})
            visita = form.save(commit=False)
            visita.agenda = agenda
            visita.save()
            messages.success(request, 'Visita agendada com sucesso!')
            return redirect(reverse('agenda:home'))
    else:
        form = VisitaForm()
    return render(request, 'agenda/agendar_visita.html', {'form': form})

# Placeholder para geração de PDF

def relatorio_pdf(request):
    messages.info(request, 'Funcionalidade de relatório PDF em desenvolvimento.')
    return redirect(reverse('agenda:home'))
