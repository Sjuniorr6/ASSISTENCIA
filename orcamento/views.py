from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Orcamento, ItemOrcamento
from decimal import Decimal
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Orcamento

# Create your views here.

class OrcamentoListView(ListView):
    model = Orcamento
    template_name = 'orcamento/orcamento.html'
    context_object_name = 'orcamentos'
    ordering = ['-data']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_name'] = self.request.GET.get('search_name', '')
        context['search_numero'] = self.request.GET.get('search_numero', '')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        search_name = self.request.GET.get('search_name')
        search_numero = self.request.GET.get('search_numero')

        if search_name:
            queryset = queryset.filter(nome__icontains=search_name)
        if search_numero:
            queryset = queryset.filter(numero__icontains=search_numero)

        return queryset

    def post(self, request, *args, **kwargs):
        try:
            # Criar o orçamento
            orcamento = Orcamento(
                numero=request.POST.get('numero'),
                data=request.POST.get('data'),
                status=request.POST.get('status'),
                nome=request.POST.get('nome'),
                telefone=request.POST.get('telefone'),
                endereco=request.POST.get('endereco'),
                cpf_cnpj=request.POST.get('cpf_cnpj'),
                bairro=request.POST.get('bairro'),
                cidade=request.POST.get('cidade'),
                observacao=request.POST.get('observacao'),
                valor_total=Decimal(request.POST.get('valor_total', '0')),
                valor_desconto=Decimal(request.POST.get('valor_desconto', '0')),
                valor_total_com_desconto=Decimal(request.POST.get('valor_total_com_desconto', '0'))
            )
            orcamento.save()

            # Processar os itens do orçamento
            quantidades = request.POST.getlist('quantidade[]')
            produtos = request.POST.getlist('produto[]')
            valores_unitarios = request.POST.getlist('valor_unitario[]')
            valores_totais = request.POST.getlist('valor_total[]')

            # Criar os itens do orçamento
            for i in range(len(quantidades)):
                if produtos[i] and quantidades[i] and valores_unitarios[i]:  # Verifica se o item não está vazio
                    item = ItemOrcamento(
                        quantidade=int(quantidades[i]),
                        produto=produtos[i],
                        valor_unitario=Decimal(valores_unitarios[i]),
                        valor_total=Decimal(valores_totais[i])
                    )
                    item.save()
                    orcamento.itens.add(item)

            messages.success(request, 'Orçamento salvo com sucesso!')
            return redirect('orcamento:lista_orcamentos')

        except Exception as e:
            messages.error(request, f'Erro ao salvar orçamento: {str(e)}')
            return self.get(request, *args, **kwargs)

def orcamento_list(request):
    try:
        orcamentos = Orcamento.objects.all().order_by('-data')
        return render(request, 'orcamento/orcamento.html', {'orcamentos': orcamentos})
    except Exception as e:
        print("Erro ao listar orçamentos:", str(e))
        return render(request, 'orcamento/orcamento.html', {'orcamentos': [], 'error': str(e)})

@csrf_exempt
def orcamento_detail(request, pk):
    try:
        print(f"Buscando orçamento com ID: {pk}")
        orcamento = get_object_or_404(Orcamento, pk=pk)
        
        if request.method == 'GET':
            # Buscar itens relacionados
            itens = orcamento.itens.all()
            print(f"Encontrados {itens.count()} itens para o orçamento {pk}")
            
            data = {
                'id': orcamento.id,
                'numero': orcamento.numero,
                'data': orcamento.data.strftime('%Y-%m-%d') if orcamento.data else '',
                'status': orcamento.status,
                'nome': orcamento.nome,
                'telefone': orcamento.telefone or '',
                'endereco': orcamento.endereco or '',
                'cpf_cnpj': orcamento.cpf_cnpj or '',
                'bairro': orcamento.bairro or '',
                'cidade': orcamento.cidade or '',
                'observacao': orcamento.observacao or '',
                'valor_total': float(orcamento.valor_total or 0),
                'valor_desconto': float(orcamento.valor_desconto or 0),
                'valor_total_com_desconto': float(orcamento.valor_total_com_desconto or 0),
                'itens': [
                    {
                        'produto': item.produto,
                        'quantidade': item.quantidade,
                        'valor_unitario': float(item.valor_unitario),
                        'valor_total': float(item.valor_total)
                    }
                    for item in itens
                ]
            }
            print("Enviando dados:", data)
            return JsonResponse(data)
            
        elif request.method == 'POST':
            try:
                data = json.loads(request.body)
                print("Dados recebidos para atualização:", data)
                
                # Atualizar dados básicos do orçamento
                orcamento.numero = data.get('numero', orcamento.numero)
                orcamento.data = data.get('data', orcamento.data)
                orcamento.status = data.get('status', orcamento.status)
                orcamento.nome = data.get('nome', orcamento.nome)
                orcamento.telefone = data.get('telefone', '')
                orcamento.endereco = data.get('endereco', '')
                orcamento.cpf_cnpj = data.get('cpf_cnpj', '')
                orcamento.bairro = data.get('bairro', '')
                orcamento.cidade = data.get('cidade', '')
                orcamento.observacao = data.get('observacao', '')
                
                # Atualizar itens
                itens_data = data.get('itens', [])
                valor_total = Decimal('0')
                
                # Remover itens antigos
                orcamento.itens.all().delete()
                
                # Adicionar novos itens
                for item_data in itens_data:
                    quantidade = int(item_data.get('quantidade', 0))
                    produto = item_data.get('produto', '').strip()
                    valor_unitario = Decimal(str(item_data.get('valor_unitario', '0')))
                    valor_total_item = quantidade * valor_unitario
                    
                    item = ItemOrcamento.objects.create(
                        quantidade=quantidade,
                        produto=produto,
                        valor_unitario=valor_unitario,
                        valor_total=valor_total_item
                    )
                    
                    orcamento.itens.add(item)
                    valor_total += valor_total_item
                
                # Atualizar valores totais
                orcamento.valor_total = valor_total
                orcamento.valor_desconto = Decimal(str(data.get('valor_desconto', '0')))
                orcamento.valor_total_com_desconto = valor_total - orcamento.valor_desconto
                orcamento.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Orçamento atualizado com sucesso!'
                })
                
            except json.JSONDecodeError as e:
                print("Erro ao decodificar JSON:", str(e))
                return JsonResponse({
                    'status': 'error',
                    'message': 'Dados inválidos'
                }, status=400)
            except Exception as e:
                print("Erro ao atualizar orçamento:", str(e))
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)
                
    except Exception as e:
        print("Erro ao processar requisição:", str(e))
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def orcamento_create(request):
    if request.method == 'POST':
        try:
            print("Dados recebidos:", request.POST)  # Debug
            print("Arquivos recebidos:", request.FILES)  # Debug
            
            # Obter dados do formulário
            numero = request.POST.get('numero')
            data = request.POST.get('data')
            status = request.POST.get('status', 'aberto')
            nome = request.POST.get('nome')
            telefone = request.POST.get('telefone')
            endereco = request.POST.get('endereco')
            cpf_cnpj = request.POST.get('cpf_cnpj')
            bairro = request.POST.get('bairro')
            cidade = request.POST.get('cidade')
            observacao = request.POST.get('observacao', '')
            valor_desconto = Decimal(request.POST.get('valor_desconto', '0'))
            
            # Validar dados obrigatórios
            if not all([numero, data, nome]):
                raise ValidationError('Número, data e nome são campos obrigatórios')
            
            # Calcular valor total dos itens
            itens_json = request.POST.get('itens', '[]')
            print("JSON dos itens:", itens_json)  # Debug
            itens_data = json.loads(itens_json)
            valor_total = Decimal('0')
            
            if not itens_data:
                raise ValidationError('É necessário adicionar pelo menos um item ao orçamento')
            
            # Criar orçamento
            orcamento = Orcamento.objects.create(
                numero=numero,
                data=data,
                status=status,
                nome=nome,
                telefone=telefone or '',
                endereco=endereco or '',
                cpf_cnpj=cpf_cnpj or '',
                bairro=bairro or '',
                cidade=cidade or '',
                observacao=observacao,
                valor_total=valor_total,
                valor_desconto=valor_desconto,
                valor_total_com_desconto=valor_total - valor_desconto
            )
            
            # Criar itens do orçamento
            for item_data in itens_data:
                quantidade = int(item_data.get('quantidade', 0))
                produto = item_data.get('produto', '').strip()
                valor_unitario = Decimal(str(item_data.get('valor_unitario', '0')))
                
                if not all([quantidade, produto, valor_unitario]):
                    raise ValidationError('Todos os campos do item são obrigatórios')
                
                valor_total_item = quantidade * valor_unitario
                
                item = ItemOrcamento.objects.create(
                    quantidade=quantidade,
                    produto=produto,
                    valor_unitario=valor_unitario,
                    valor_total=valor_total_item
                )
                
                orcamento.itens.add(item)
                valor_total += valor_total_item
            
            # Atualizar valor total do orçamento
            orcamento.valor_total = valor_total
            orcamento.valor_total_com_desconto = valor_total - valor_desconto
            orcamento.save()
            
            print("Orçamento criado com sucesso:", orcamento.id)  # Debug
            return JsonResponse({'status': 'success', 'message': 'Orçamento criado com sucesso!'})
            
        except ValidationError as e:
            print("Erro de validação:", str(e))  # Debug
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except json.JSONDecodeError as e:
            print("Erro ao decodificar JSON:", str(e))  # Debug
            return JsonResponse({'status': 'error', 'message': 'Erro ao processar dados dos itens'}, status=400)
        except Exception as e:
            print("Erro ao criar orçamento:", str(e))  # Debug
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)

def orcamento_pdf(request, pk):
    orcamento = get_object_or_404(Orcamento, pk=pk)
    return JsonResponse({'status': 'success', 'message': 'Geração de PDF ainda não implementada'})

def index(request):
    orcamentos = Orcamento.objects.all().order_by('-id')
    return render(request, 'orcamento/orcamento.html', {'orcamentos': orcamentos})

@csrf_exempt
@require_http_methods(["POST"])
def criar_orcamento(request):
    if request.method == 'POST':
        try:
            print("=== INÍCIO DO PROCESSAMENTO ===")
            # Extrai os dados do formulário
            dados = request.POST.dict()
            print("Dados recebidos:", dados)
            
            # Remove campos que não pertencem ao modelo
            campos_remover = [
                'csrfmiddlewaretoken',
                'itens',
                'produto[]',
                'quantidade[]',
                'valor_unitario[]',
                'valor_total[]'
            ]
            
            for campo in campos_remover:
                dados.pop(campo, None)
            
            print("Dados após limpeza:", dados)
            
            # Converte valores decimais
            campos_decimais = ['valor_total', 'valor_desconto', 'valor_total_com_desconto']
            for campo in campos_decimais:
                if campo in dados:
                    try:
                        valor = dados[campo].strip() or '0'
                        dados[campo] = Decimal(valor)
                        print(f"Convertido {campo}: {dados[campo]}")
                    except Exception as e:
                        print(f"Erro ao converter {campo}: {str(e)}")
                        dados[campo] = Decimal('0')

            try:
                print("Tentando criar orçamento com dados:", dados)
                # Tenta criar o orçamento
                orcamento = Orcamento.objects.create(**dados)
                print("Orçamento criado com ID:", orcamento.id)
                
                # Processa os itens
                itens_json = request.POST.get('itens', '[]')
                print("JSON dos itens:", itens_json)
                itens = json.loads(itens_json)
                print("Itens decodificados:", itens)
                
                for item in itens:
                    try:
                        quantidade = int(item.get('quantidade', 0))
                        valor_unitario = Decimal(str(item.get('valor_unitario', '0')))
                        valor_total = Decimal(str(item.get('valor_total', '0')))
                        
                        item_criado = ItemOrcamento.objects.create(
                            orcamento=orcamento,
                            produto=item.get('produto', ''),
                            quantidade=quantidade,
                            valor_unitario=valor_unitario,
                            valor_total=valor_total
                        )
                        print(f"Item criado: {item_criado}")
                    except Exception as e:
                        print(f"Erro ao processar item: {str(e)}")
                        continue
                
                print("=== PROCESSAMENTO CONCLUÍDO COM SUCESSO ===")
                return JsonResponse({
                    'status': 'success',
                    'message': 'Orçamento criado com sucesso!',
                    'id': orcamento.id
                })
                
            except IntegrityError as e:
                print(f"Erro de integridade: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Já existe um orçamento com este número. Por favor, use um número diferente.'
                }, status=400)
                
        except Exception as e:
            print(f"Erro geral: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao criar orçamento: {str(e)}'
            }, status=400)
    
    print("Método não permitido")        
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido'
    }, status=405)

@require_http_methods(["GET"])
def get_orcamento(request, id):
    try:
        orcamento = get_object_or_404(Orcamento, id=id)
        itens = orcamento.itens.all()
        
        data = {
            'id': orcamento.id,
            'numero': orcamento.numero,
            'data': orcamento.data.strftime('%Y-%m-%d'),
            'status': orcamento.status,
            'nome': orcamento.nome,
            'telefone': orcamento.telefone,
            'endereco': orcamento.endereco,
            'cpf_cnpj': orcamento.cpf_cnpj,
            'bairro': orcamento.bairro,
            'cidade': orcamento.cidade,
            'observacao': orcamento.observacao,
            'valor_desconto': orcamento.valor_desconto,
            'itens': [{
                'produto': item.produto,
                'quantidade': item.quantidade,
                'valor_unitario': float(item.valor_unitario)
            } for item in itens]
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def atualizar_orcamento(request, id):
    try:
        print("=== INÍCIO DA ATUALIZAÇÃO ===")
        orcamento = get_object_or_404(Orcamento, id=id)
        print(f"Orçamento encontrado: {orcamento}")
        
        # Extrai dados do formulário
        dados = request.POST.dict()
        print("Dados recebidos:", dados)
        
        # Remove campos que não pertencem ao modelo
        campos_remover = [
            'csrfmiddlewaretoken',
            'itens',
            'modal_produto[]',
            'modal_quantidade[]',
            'modal_valor_unitario[]',
            'modal_valor_total[]'
        ]
        
        for campo in campos_remover:
            dados.pop(campo, None)
        
        print("Dados após limpeza:", dados)
        
        # Converte valores decimais
        campos_decimais = ['valor_total', 'valor_desconto', 'valor_total_com_desconto']
        for campo in campos_decimais:
            if campo in dados:
                try:
                    valor = dados[campo].strip() or '0'
                    dados[campo] = Decimal(valor)
                    print(f"Convertido {campo}: {dados[campo]}")
                except Exception as e:
                    print(f"Erro ao converter {campo}: {str(e)}")
                    dados[campo] = Decimal('0')
        
        # Atualiza o orçamento
        for key, value in dados.items():
            setattr(orcamento, key, value)
        orcamento.save()
        print("Orçamento atualizado")
        
        # Processa os itens
        itens_json = request.POST.get('itens', '[]')
        print("JSON dos itens:", itens_json)
        itens = json.loads(itens_json)
        print("Itens decodificados:", itens)
        
        # Remove itens antigos
        orcamento.itens.all().delete()
        print("Itens antigos removidos")
        
        # Cria novos itens
        valor_total_geral = Decimal('0')
        for item in itens:
            try:
                quantidade = int(item.get('quantidade', 0))
                valor_unitario = Decimal(str(item.get('valor_unitario', '0')))
                valor_total = quantidade * valor_unitario  # Calcula o valor total
                
                item_criado = ItemOrcamento.objects.create(
                    orcamento=orcamento,
                    produto=item.get('produto', ''),
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    valor_total=valor_total
                )
                print(f"Item criado: {item_criado}")
                valor_total_geral += valor_total
            except Exception as e:
                print(f"Erro ao processar item: {str(e)}")
                continue
        
        # Atualiza o valor total do orçamento
        orcamento.valor_total = valor_total_geral
        orcamento.valor_total_com_desconto = valor_total_geral - orcamento.valor_desconto
        orcamento.save()
        
        print("=== ATUALIZAÇÃO CONCLUÍDA COM SUCESSO ===")
        return JsonResponse({
            'status': 'success',
            'message': 'Orçamento atualizado com sucesso!'
        })
        
    except Exception as e:
        print(f"Erro geral na atualização: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao atualizar orçamento: {str(e)}'
        }, status=400)

def lista_orcamentos(request):
    search_name = request.GET.get('search_name', '')
    search_numero = request.GET.get('search_numero', '')
    
    orcamentos = Orcamento.objects.all().order_by('-data')
    
    if search_name:
        orcamentos = orcamentos.filter(nome__icontains=search_name)
    if search_numero:
        orcamentos = orcamentos.filter(numero__icontains=search_numero)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'orcamento/partials/lista_orcamentos.html', {'orcamentos': orcamentos})

    context = {
        'orcamentos': orcamentos,
        'search_name': search_name,
        'search_numero': search_numero,
        'active_tab': 'orcamento'
    }
    return render(request, 'orcamento/orcamento.html', context)

def novo_orcamento(request):
    if request.method == 'POST':
        return orcamento_create(request)
    
    return render(request, 'orcamento/novo_orcamento.html')

def detalhe_orcamento(request, orcamento_id):
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    itens = orcamento.itens.all()
    
    data = {
        'id': orcamento.id,
        'numero': orcamento.numero,
        'data': orcamento.data.strftime('%Y-%m-%d'),
        'status': orcamento.status,
        'nome': orcamento.nome,
        'telefone': orcamento.telefone,
        'endereco': orcamento.endereco,
        'cpf_cnpj': orcamento.cpf_cnpj,
        'bairro': orcamento.bairro,
        'cidade': orcamento.cidade,
        'valor_total': float(orcamento.valor_total),
        'valor_desconto': float(orcamento.valor_desconto),
        'valor_total_com_desconto': float(orcamento.valor_total_com_desconto),
        'observacao': orcamento.observacao,
        'itens': [{
            'produto': item.produto,
            'quantidade': item.quantidade,
            'valor_unitario': float(item.valor_unitario),
            'valor_total': float(item.valor_total)
        } for item in itens]
    }
    
    return JsonResponse(data)

def safe_decimal(value, default='0'):
    """Convert a value to Decimal safely"""
    try:
        # Remove any currency symbols and spaces
        if isinstance(value, str):
            value = value.replace('R$', '').replace(' ', '')
        return Decimal(value or default)
    except:
        return Decimal(default)

def salvar_orcamento(request):
    if request.method == 'POST':
        try:
            # Extrair dados do formulário
            data = {
                'numero': request.POST.get('numero'),
                'data': request.POST.get('data'),
                'status': request.POST.get('status'),
                'nome': request.POST.get('nome'),
                'telefone': request.POST.get('telefone'),
                'endereco': request.POST.get('endereco'),
                'cpf_cnpj': request.POST.get('cpf_cnpj'),
                'bairro': request.POST.get('bairro'),
                'cidade': request.POST.get('cidade'),
                'observacao': request.POST.get('observacao'),
                'valor_total': safe_decimal(request.POST.get('valor_total')),
                'valor_desconto': safe_decimal(request.POST.get('valor_desconto')),
                'valor_total_com_desconto': safe_decimal(request.POST.get('valor_total_com_desconto'))
            }

            # Criar ou atualizar orçamento
            orcamento_id = request.POST.get('id')
            if orcamento_id:
                orcamento = Orcamento.objects.get(id=orcamento_id)
                for key, value in data.items():
                    setattr(orcamento, key, value)
                orcamento.save()
                # Limpar itens existentes
                orcamento.itens.all().delete()
            else:
                orcamento = Orcamento.objects.create(**data)

            # Processar itens
            quantidades = request.POST.getlist('quantidade[]')
            produtos = request.POST.getlist('produto[]')
            valores = request.POST.getlist('valor_unitario[]')

            for i in range(len(quantidades)):
                if quantidades[i] and produtos[i] and valores[i]:
                    ItemOrcamento.objects.create(
                        orcamento=orcamento,
                        quantidade=safe_decimal(quantidades[i]),
                        produto=produtos[i],
                        valor_unitario=safe_decimal(valores[i])
                    )

            messages.success(request, 'Orçamento salvo com sucesso!')
            return redirect('orcamento:lista_orcamentos')

        except Exception as e:
            messages.error(request, f'Erro ao salvar orçamento: {str(e)}')
            return redirect('orcamento:lista_orcamentos')

    return redirect('orcamento:lista_orcamentos')

def faturamento_orcamentos_pagos(dias=30):
    data_inicio = timezone.now().date() - timedelta(days=dias)
    return Orcamento.objects.filter(
        status__iexact='PAGO',
        data__gte=data_inicio
    ).aggregate(total=Sum('valor_total_com_desconto'))['total'] or 0

# Exemplo de uso na view do dashboard:
# faturamento = faturamento_orcamentos_pagos(dias=30)
