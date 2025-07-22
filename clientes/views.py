from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from .models import Clientes
from .forms import ClientesForm
import json
from django.template.loader import render_to_string
from django.http import HttpResponse

@login_required
def clientes_view(request):
    """
    Renderiza a página de clientes e lida com a criação de novos clientes.
    """
    # Busca
    search_name = request.GET.get('search_name', '')
    search_os = request.GET.get('search_os', '')
    
    # Query base
    clientes = Clientes.objects.all().order_by('-id')
    
    # Aplicar filtros de busca
    if search_name:
        clientes = clientes.filter(
            Q(nome__icontains=search_name) |
            Q(cpf_cnpj__icontains=search_name) |
            Q(telefone__icontains=search_name)
        )
    
    if search_os:
        clientes = clientes.filter(numero_os__icontains=search_os)
    
    context = {
        'clientes': clientes,
        'search_name': search_name,
        'search_os': search_os,
        'active_tab': 'clientes',
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('clientes/partials/lista_clientes.html', context, request=request)
        return HttpResponse(html)
    return render(request, 'clientes/clientes.html', context)

@login_required
def carregar_mais_clientes(request):
    """View para carregar mais clientes via AJAX (scroll infinito)"""
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))
    search_name = request.GET.get('search_name', '')
    search_os = request.GET.get('search_os', '')
    
    clientes = Clientes.objects.all().order_by('-id')
    
    # Aplicar filtros
    if search_name:
        clientes = clientes.filter(
            Q(nome__icontains=search_name) |
            Q(cpf_cnpj__icontains=search_name) |
            Q(telefone__icontains=search_name)
        )
    
    if search_os:
        clientes = clientes.filter(numero_os__icontains=search_os)
    
    # Aplicar offset e limit
    clientes_paginados = clientes[offset:offset + limit]
    
    # Renderizar apenas os itens da lista
    html = render(request, 'clientes/partials/lista_clientes_items.html', {
        'clientes': clientes_paginados
    }).content.decode('utf-8')
    
    return JsonResponse({
        'html': html,
        'has_more': len(clientes_paginados) == limit,
        'total_count': clientes.count()
    })

@login_required
def salvar_cliente(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('id')
        
        if cliente_id:
            # Atualizar cliente existente
            cliente = get_object_or_404(Clientes, id=cliente_id)
            form = ClientesForm(request.POST, instance=cliente)
            action = 'atualizado'
        else:
            # Criar novo cliente
            form = ClientesForm(request.POST)
            action = 'criado'
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente {action} com sucesso!')
        else:
            messages.error(request, 'Erro ao salvar cliente. Verifique os dados.')
    
    return redirect('clientes:clientes')

@login_required
def get_cliente(request, cliente_id):
    """
    Retorna os dados de um cliente específico em formato JSON para o formulário.
    """
    try:
        cliente = get_object_or_404(Clientes, id=cliente_id)
        data = {
            'id': cliente.id,
            'numero_os': cliente.numero_os or '',
            'data_chamado': cliente.data_chamado.strftime('%Y-%m-%d') if cliente.data_chamado else '',
            'status_servico': cliente.status_servico or '',
            'nome': cliente.nome or '',
            'cpf_cnpj': cliente.cpf_cnpj or '',
            'telefone': cliente.telefone or '',
            'celular': cliente.celular or '',
            'email': cliente.email or '',
            'apto_bloco': cliente.apto_bloco or '',
            'endereco': cliente.endereco or '',
            'bairro': cliente.bairro or '',
            'cidade': cliente.cidade or '',
            'cep': cliente.cep or '',
            'revendedor': cliente.revendedor or '',
            'tecnicos': cliente.tecnicos or '',
            'periodo': cliente.periodo or '',
            'data_instalacao': cliente.data_instalacao.strftime('%Y-%m-%d') if cliente.data_instalacao else '',
            'valor_total': str(cliente.valor_total) if cliente.valor_total is not None else '',
            'forma_pagamento': cliente.forma_pagamento or '',
            'servicos': cliente.servicos or '',
            'relatorios_servicos_prestados': cliente.relatorios_servicos_prestados or '',
        }
        return JsonResponse({'success': True, 'cliente': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def atualizar_cliente(request, cliente_id):
    """
    Atualiza um cliente existente a partir de dados POST.
    """
    if request.method == 'POST':
        cliente = get_object_or_404(Clientes, id=cliente_id)
        form = ClientesForm(request.POST, instance=cliente)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
        else:
            messages.error(request, 'Erro ao atualizar cliente.')
    
    return redirect('clientes:clientes')