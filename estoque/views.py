from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Estoque
from .forms import EstoqueForm
from django.db.models import Q
import json

@login_required
def estoque(request):
    if request.method == 'POST':
        form = EstoqueForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    form = EstoqueForm()
    
    # Lógica de busca
    query_nome = request.GET.get('nome')
    query_registro = request.GET.get('registro')
    itens = Estoque.objects.all()

    if query_nome:
        itens = itens.filter(nome_peca__icontains=query_nome)
    if query_registro:
        itens = itens.filter(id__icontains=query_registro)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and (query_nome or query_registro):
        html = render_to_string(
            'estoque/partials/lista_estoque.html', {'itens': itens}
        )
        return JsonResponse({'html': html})

    context = {'form': form, 'itens': itens}
    return render(request, 'estoque/estoque.html', context)

@login_required
def get_item_details(request, item_id):
    item = get_object_or_404(Estoque, id=item_id)
    data = {
        'id': item.id,
        'nome_peca': item.nome_peca,
        'codigo': item.codigo,
        'modelo': item.modelo,
        'fornecedor': item.fornecedor,
        'data_entrada': item.data_entrada.strftime('%Y-%m-%d'),
        'descricao': item.descricao,
        'status': item.status,
        'status_display': item.get_status_display(),
    }
    return JsonResponse(data)

@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Estoque, id=item_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        form = EstoqueForm(data, instance=item)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Estoque, id=item_id)
    if request.method == 'POST':
        item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})

@login_required
def get_estoque(request, estoque_id):
    """Retorna os dados de um item do estoque para carregar no formulário"""
    try:
        estoque = get_object_or_404(Estoque, id=estoque_id)
        data = {
            'success': True,
            'estoque': {
                'id': estoque.id,
                'id_registro': estoque.id,
                'nome_peca': estoque.nome_peca,
                'codigo': estoque.codigo,
                'modelo': estoque.modelo,
                'fornecedor': estoque.fornecedor,
                'data_entrada': estoque.data_entrada.strftime('%Y-%m-%d') if estoque.data_entrada else '',
                'descricao': estoque.descricao,
                'status': estoque.status,
                'status_display': estoque.get_status_display(),
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def atualizar_estoque(request, estoque_id):
    """Atualiza um item do estoque"""
    if request.method == 'POST':
        try:
            estoque = get_object_or_404(Estoque, id=estoque_id)
            form = EstoqueForm(request.POST, instance=estoque)
            if form.is_valid():
                form.save()
                return redirect('estoque:estoque')
            else:
                # Se houver erros, renderiza a página com os erros
                context = {
                    'form': form,
                    'itens': Estoque.objects.all(),
                    'search_name': request.GET.get('search_name', ''),
                    'search_registro': request.GET.get('search_registro', '')
                }
                return render(request, 'estoque/estoque.html', context)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return redirect('estoque:estoque')
