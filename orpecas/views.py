from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q, Sum
from .models import Orpecas, ItemOrpecas
from .forms import OrpecasForm
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class OrpecasView(View):
    def get(self, request):
        search_name = request.GET.get('search_name', '')
        search_numero = request.GET.get('search_numero', '')

        orpecas_list = Orpecas.objects.all()

        if search_name:
            orpecas_list = orpecas_list.filter(
                Q(nome_cliente__icontains=search_name) |
                Q(cpf_cnpj__icontains=search_name) |
                Q(telefone__icontains=search_name)
            )
        
        if search_numero:
            orpecas_list = orpecas_list.filter(numero__icontains=search_numero)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(
                'orpecas/partials/lista_orpecas.html',
                {
                    'orpecas_list': orpecas_list,
                    'search_name': search_name,
                    'search_numero': search_numero,
                }
            )
            return JsonResponse({'html': html})

        form = OrpecasForm()
        context = {
            'orpecas_list': orpecas_list,
            'form': form,
            'search_name': search_name,
            'search_numero': search_numero,
        }
        return render(request, 'orpecas/orpecas.html', context)

    def post(self, request):
        form = OrpecasForm(request.POST)
        if form.is_valid():
            orpecas = form.save(commit=False)
            # Salva o objeto principal para obter um ID antes de adicionar os itens
            orpecas.save() 
            # Agora processa e salva os itens, que podem ser vinculados ao ID do orçamento
            self._process_items(request, orpecas)
            # Salva novamente para atualizar os campos de totais calculados em _process_items
            orpecas.save()
            return redirect('orpecas:orpecas')
        
        # Se inválido, renderiza novamente com erros
        orpecas_list = Orpecas.objects.all()
        context = {'orpecas_list': orpecas_list, 'form': form}
        return render(request, 'orpecas/orpecas.html', context)

    def _process_items(self, request, orpecas):
        produtos = request.POST.getlist('produto[]')
        quantidades = request.POST.getlist('quantidade[]')
        valores_unitarios = request.POST.getlist('valor_unitario[]')
        
        valor_total_orcamento = Decimal(0)
        
        # Se for uma atualização, limpa itens antigos
        if orpecas.pk:
            orpecas.itens.all().delete()
            
        for produto, qtd_str, valor_str in zip(produtos, quantidades, valores_unitarios):
            if produto and qtd_str and valor_str:
                quantidade = Decimal(qtd_str)
                valor_unitario = Decimal(valor_str)
                ItemOrpecas.objects.create(
                    orpecas=orpecas,
                    produto=produto,
                    quantidade=quantidade,
                    valor_unitario=valor_unitario
                )
                valor_total_orcamento += quantidade * valor_unitario
        
        orpecas.valor_total = valor_total_orcamento
        desconto = Decimal(request.POST.get('valor_desconto', '0'))
        orpecas.valor_desconto = desconto
        orpecas.valor_total_com_desconto = valor_total_orcamento - desconto


def get_orpecas(request, orpecas_id):
    orpecas = get_object_or_404(Orpecas.objects.prefetch_related('itens'), id=orpecas_id)
    data = {
        'id': orpecas.id,
        'numero': orpecas.numero,
        'data': orpecas.data.strftime('%Y-%m-%d'),
        'status': orpecas.status,
        'nome_cliente': orpecas.nome_cliente,
        'telefone': orpecas.telefone,
        'cpf_cnpj': orpecas.cpf_cnpj,
        'endereco': orpecas.endereco,
        'bairro': orpecas.bairro,
        'cidade': orpecas.cidade,
        'observacao': orpecas.observacao,
        'valor_total': f'{orpecas.valor_total:.2f}',
        'valor_desconto': f'{orpecas.valor_desconto:.2f}',
        'valor_total_com_desconto': f'{orpecas.valor_total_com_desconto:.2f}',
        'itens': [{
            'produto': item.produto,
            'quantidade': item.quantidade,
            'valor_unitario': f'{item.valor_unitario:.2f}'
        } for item in orpecas.itens.all()]
    }
    return JsonResponse(data)

def atualizar_orpecas(request, orpecas_id):
    orpecas = get_object_or_404(Orpecas, id=orpecas_id)
    if request.method == 'POST':
        form = OrpecasForm(request.POST, instance=orpecas)
        if form.is_valid():
            updated_orpecas = form.save(commit=False)
            view = OrpecasView()
            view._process_items(request, updated_orpecas)
            updated_orpecas.save()
            return redirect('orpecas:orpecas')
    return redirect('orpecas:orpecas')

def excluir_orpecas(request, orpecas_id):
    orpecas = get_object_or_404(Orpecas, id=orpecas_id)
    if request.method == 'POST':
        orpecas.delete()
    return redirect('orpecas:orpecas')

def faturamento_orpecas_pagos(dias=30):
    data_inicio = timezone.now().date() - timedelta(days=dias)
    return Orpecas.objects.filter(
        status__iexact='PAGO',
        data__gte=data_inicio
    ).aggregate(total=Sum('valor_total_com_desconto'))['total'] or 0

# Exemplo de uso na view do dashboard:
# faturamento = faturamento_orpecas_pagos(dias=30)
