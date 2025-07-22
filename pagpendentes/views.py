from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse, Http404
from django.apps import apps
from django.db.models import Q
from itertools import chain
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.cache import never_cache

# Create your views here.

class PagamentosPendentesView(LoginRequiredMixin, View):
    def get(self, request):
        # Mapeia o nome do modelo para o campo de status correto
        status_field_map = {
            'clientes': 'status_servico',
            'orcamento': 'status',
            'rat': 'status',
            'orpecas': 'status',
        }
        
        pending_items = []

        # Itera sobre os modelos e busca itens pendentes
        for app_name, model_name in [('clientes', 'Clientes'), ('orcamento', 'Orcamento'), ('rat', 'Rat'), ('orpecas', 'Orpecas')]:
            try:
                Model = apps.get_model(app_label=app_name, model_name=model_name)
                status_field = status_field_map[app_name]
                
                # Constrói a query do filtro dinamicamente
                query = Q(**{f"{status_field}__iexact": "pendente_pagamento"})
                
                items = Model.objects.filter(query)
                
                # Adiciona uma propriedade para saber o tipo e o nome do cliente
                for item in items:
                    item.content_type = f"{app_name}.{model_name}".lower()
                    
                    # Adiciona um nome amigável para o tipo de documento
                    type_map = {
                        'clientes': 'OS',
                        'orcamento': 'Orçamento',
                        'rat': 'RAT',
                        'orpecas': 'Orç. Peças'
                    }
                    item.display_type_verbose = type_map.get(app_name, 'N/A')

                    # Padroniza o acesso aos campos para exibição
                    # A ordem é importante para pegar o nome correto de cada modelo.
                    if hasattr(item, 'cliente') and item.cliente:
                        # Para RAT, que tem um ForeignKey para o modelo Clientes
                        item.display_cliente_nome = item.cliente.nome
                        # Copiar dados do cliente relacionado
                        item.display_cpf_cnpj = getattr(item.cliente, 'cpf_cnpj', 'N/A')
                        item.display_telefone = getattr(item.cliente, 'telefone', 'N/A')
                        item.display_celular = getattr(item.cliente, 'celular', 'N/A')
                        item.display_email = getattr(item.cliente, 'email', 'N/A')
                        item.display_apto_bloco = getattr(item.cliente, 'apto_bloco', 'N/A')
                        item.display_endereco = getattr(item.cliente, 'endereco', 'N/A')
                        item.display_bairro = getattr(item.cliente, 'bairro', 'N/A')
                        item.display_cidade = getattr(item.cliente, 'cidade', 'N/A')
                        item.display_cep = getattr(item.cliente, 'cep', 'N/A')
                    elif hasattr(item, 'nome_cliente'):
                        # Para Orpecas, que usa 'nome_cliente'
                        item.display_cliente_nome = item.nome_cliente
                        # Campos específicos do Orpecas
                        item.display_cpf_cnpj = getattr(item, 'cpf_cnpj', 'N/A')
                        item.display_telefone = getattr(item, 'telefone', 'N/A')
                        item.display_celular = getattr(item, 'celular', 'N/A')
                        item.display_email = getattr(item, 'email', 'N/A')
                        item.display_apto_bloco = getattr(item, 'apto_bloco', 'N/A')
                        item.display_endereco = getattr(item, 'endereco', 'N/A')
                        item.display_bairro = getattr(item, 'bairro', 'N/A')
                        item.display_cidade = getattr(item, 'cidade', 'N/A')
                        item.display_cep = getattr(item, 'cep', 'N/A')
                    elif hasattr(item, 'nome'):
                        # Para Clientes (OS) e Orcamento, que usam 'nome'
                        item.display_cliente_nome = item.nome
                        # Campos específicos do Clientes/Orcamento
                        item.display_cpf_cnpj = getattr(item, 'cpf_cnpj', 'N/A')
                        item.display_telefone = getattr(item, 'telefone', 'N/A')
                        item.display_celular = getattr(item, 'celular', 'N/A')
                        item.display_email = getattr(item, 'email', 'N/A')
                        item.display_apto_bloco = getattr(item, 'apto_bloco', 'N/A')
                        item.display_endereco = getattr(item, 'endereco', 'N/A')
                        item.display_bairro = getattr(item, 'bairro', 'N/A')
                        item.display_cidade = getattr(item, 'cidade', 'N/A')
                        item.display_cep = getattr(item, 'cep', 'N/A')
                    else:
                        item.display_cliente_nome = 'N/A'
                        item.display_cpf_cnpj = 'N/A'
                        item.display_telefone = 'N/A'
                        item.display_celular = 'N/A'
                        item.display_email = 'N/A'
                        item.display_apto_bloco = 'N/A'
                        item.display_endereco = 'N/A'
                        item.display_bairro = 'N/A'
                        item.display_cidade = 'N/A'
                        item.display_cep = 'N/A'
                        
                    item.display_numero = getattr(item, 'numero_os', getattr(item, 'numero', getattr(item, 'numero_rat', 'N/A')))
                    item.display_data = getattr(item, 'data_chamado', getattr(item, 'data', getattr(item, 'data_visita', None)))
                    item.display_valor = getattr(item, 'valor_total', getattr(item, 'valor_total_com_desconto', 0))

                    # Campos de serviço
                    item.display_revendedor = getattr(item, 'revendedor', 'N/A')
                    item.display_tecnicos = getattr(item, 'tecnicos', 'N/A')
                    item.display_periodo = getattr(item, 'periodo', 'N/A')
                    item.display_data_instalacao = getattr(item, 'data_instalacao', 'N/A')
                    item.display_forma_pagamento = getattr(item, 'forma_pagamento', 'N/A')
                    item.display_servicos = getattr(item, 'servicos', 'N/A')
                    item.display_relatorios = getattr(item, 'relatorios_servicos_prestados', 'N/A')

                    # Padroniza o status display
                    if hasattr(item, 'get_status_servico_display'):
                        item.display_status = item.get_status_servico_display()
                    elif hasattr(item, 'get_status_display'):
                        item.display_status = item.get_status_display()
                    else:
                        item.display_status = 'N/A'

                    # Padroniza o campo de observação, buscando em diferentes atributos possíveis
                    obs = getattr(item, 'observacao', None) or \
                          getattr(item, 'servicos', None) or \
                          getattr(item, 'relatorios_servicos_prestados', None) or \
                          getattr(item, 'servico_a_executar', None) or \
                          ''
                    item.display_observacao = obs

                    # Debug: mostrar alguns itens
                    if len(pending_items) < 3:  # Mostrar apenas os primeiros 3 para debug
                        print(f"Item {app_name}: nome='{item.display_cliente_nome}', numero='{item.display_numero}', valor={item.display_valor}")

                pending_items.extend(items)
            except LookupError:
                # O modelo ou app não existe, ignora
                continue
        
        # Ordena a lista combinada por data (mais recentes primeiro)
        pending_items.sort(key=lambda x: x.display_data, reverse=True)

        # Filtros de pesquisa
        search_name = request.GET.get('search_name', '')
        search_numero = request.GET.get('search_numero', '')

        print(f"=== DEBUG PAGPENDENTES ===")
        print(f"search_name: '{search_name}'")
        print(f"search_numero: '{search_numero}'")
        print(f"source: '{request.GET.get('source')}'")
        print(f"Total de itens antes do filtro: {len(pending_items)}")

        if search_name:
            pending_items = [
                item for item in pending_items
                if search_name.lower() in item.display_cliente_nome.lower()
            ]
            print(f"Após filtro por nome: {len(pending_items)} itens")

        if search_numero:
            # Garante que a comparação seja feita com strings
            pending_items = [
                item for item in pending_items
                if search_numero.lower() in str(item.display_numero).lower()
            ]
            print(f"Após filtro por número: {len(pending_items)} itens")
        
        context = {
            'pending_items': pending_items,
            'search_name': search_name,
            'search_numero': search_numero,
        }

        # Se for uma requisição via JS (busca), retorna apenas o parcial
        if request.GET.get('source') == 'js':
            return render(request, 'pagpendentes/partials/lista_pagamentos.html', context)

        return render(request, 'pagpendentes/pagpendentes.html', context)

@never_cache
@login_required
def marcar_como_pago(request):
    if request.method == 'POST':
        item_type = request.POST.get('content_type')
        item_id = request.POST.get('id')
        new_status = request.POST.get('new_status', 'pago')

        if not item_type or not item_id:
            return JsonResponse({'success': False, 'error': 'Dados inválidos.'}, status=400)

        try:
            app_label, model_name = item_type.split('.')
            Model = apps.get_model(app_label=app_label, model_name=model_name)
            
            item = get_object_or_404(Model, id=item_id)
            
            # Determina o nome do campo de status
            status_field = 'status_servico' if app_label == 'clientes' else 'status'
            
            # Atualiza o status para o valor selecionado
            if hasattr(item, status_field):
                setattr(item, status_field, new_status)
                item.save()
                return JsonResponse({'success': True})
            else:
                 return JsonResponse({'success': False, 'error': 'Campo de status não encontrado.'}, status=400)

        except (LookupError, ValueError, Http404) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Método inválido.'}, status=405)
