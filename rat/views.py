from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from .models import Rat, Clientes, RatEquipamento
from .forms import RatForm
from django.core import serializers
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

class RatView(LoginRequiredMixin, View):
    def get(self, request):
        search_name = request.GET.get('search_name')
        search_rat = request.GET.get('search_rat')

        rats = Rat.objects.all()

        if search_name:
            rats = rats.filter(
                Q(cliente__nome__icontains=search_name) |
                Q(cliente__cpf_cnpj__icontains=search_name) |
                Q(cliente__telefone__icontains=search_name)
            )
        
        if search_rat:
            rats = rats.filter(numero_rat__icontains=search_rat)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(
                'rat/partials/lista_rats.html',
                {
                    'rats': rats,
                    'search_name': search_name or '',
                    'search_rat': search_rat or '',
                },
                request=request
            )
            return HttpResponse(html)

        form = RatForm()
        clientes = Clientes.objects.all()
        equipamentos_json = None
        if 'id' in request.GET:
            try:
                rat_id = int(request.GET['id'])
                rat = Rat.objects.get(id=rat_id)
                equipamentos = rat.equipamentos.all()
                equipamentos_json = json.dumps([
                    {
                        'equipamento': e.equipamento,
                        'fabricante': e.fabricante,
                        'modelo': e.modelo,
                        'numero_serie': e.numero_serie,
                        'data_instalacao': e.data_instalacao.strftime('%Y-%m-%d') if e.data_instalacao else '',
                        'data_compra': e.data_compra.strftime('%Y-%m-%d') if e.data_compra else '',
                    } for e in equipamentos
                ])
            except Exception:
                equipamentos_json = None
        context = {
            'rats': rats,
            'form': form,
            'clientes': clientes,
            'search_name': search_name or '',
            'search_rat': search_rat or '',
            'equipamentos_json': equipamentos_json,
        }
        return render(request, 'rat/rat.html', context)

    def post(self, request):
        form = RatForm(request.POST)
        if form.is_valid():
            rat = form.save()
            # Limpa equipamentos antigos (caso edição)
            RatEquipamento.objects.filter(rat=rat).delete()
            # Salvar equipamentos dinâmicos
            equipamentos = zip(
                request.POST.getlist('equipamento[]'),
                request.POST.getlist('fabricante[]'),
                request.POST.getlist('modelo[]'),
                request.POST.getlist('numero_serie[]'),
                request.POST.getlist('data_instalacao[]'),
                request.POST.getlist('data_compra[]'),
            )
            for eq, fab, mod, num, data_inst, data_comp in equipamentos:
                if eq.strip():
                    RatEquipamento.objects.create(
                        rat=rat,
                        equipamento=eq,
                        fabricante=fab,
                        modelo=mod,
                        numero_serie=num,
                        data_instalacao=data_inst or None,
                        data_compra=data_comp or None,
                    )
            return redirect('rat:rat')
        
        # Se o formulário for inválido, renderiza a página novamente com os erros
        rats = Rat.objects.all()
        clientes = Clientes.objects.all()
        context = {
            'rats': rats,
            'form': form,
            'clientes': clientes,
        }
        return render(request, 'rat/rat.html', context)

@never_cache
@login_required
def get_rat(request, rat_id):
    try:
        rat = get_object_or_404(Rat, id=rat_id)
        cliente = rat.cliente
        equipamentos = rat.equipamentos.all()
        equipamentos_list = [
            {
                'equipamento': e.equipamento,
                'fabricante': e.fabricante,
                'modelo': e.modelo,
                'numero_serie': e.numero_serie,
                'data_instalacao': e.data_instalacao.strftime('%Y-%m-%d') if e.data_instalacao else '',
                'data_compra': e.data_compra.strftime('%Y-%m-%d') if e.data_compra else '',
            } for e in equipamentos
        ]
        rat_data = {
            'success': True,
            'rat': {
                'id': rat.id,
                'cliente_id': cliente.id,
                'cliente_nome': cliente.nome,
                'cliente_telefone': cliente.telefone,
                'cliente_celular': cliente.celular,
                'cliente_email': cliente.email,
                'cliente_endereco': cliente.endereco,
                'cliente_bairro': cliente.bairro,
                'cliente_cidade': cliente.cidade,
                'cliente_cep': cliente.cep,
                'cliente_cpf_cnpj': cliente.cpf_cnpj,
                'numero_rat': rat.numero_rat,
                'status': rat.status,
                'data_visita': rat.data_visita.strftime('%Y-%m-%d') if rat.data_visita else '',
                'periodo': rat.periodo,
                'horario': rat.horario,
                'data_instalacao': rat.data_instalacao.strftime('%Y-%m-%d') if rat.data_instalacao else '',
                'loja_revendedora': rat.loja_revendedora,
                'data_compra': rat.data_compra.strftime('%Y-%m-%d') if rat.data_compra else '',
                'fabricante': rat.fabricante,
                'modelo': rat.modelo,
                'equipamento': rat.equipamento,
                'numero_serie': rat.numero_serie,
                'codigo_produto': rat.codigo_produto,
                'diametro_tubulacao': rat.diametro_tubulacao,
                'voltagem': rat.voltagem,
                'numero_nota_fiscal': rat.numero_nota_fiscal,
                'tipo_gas': rat.tipo_gas,
                'equipe_tecnica': rat.equipe_tecnica,
                'tipo_servico': rat.tipo_servico,
                'relatorio_interno': rat.relatorio_interno,
                'servico_a_executar': rat.servico_a_executar,
            },
            'equipamentos': equipamentos_list,
        }
        return JsonResponse(rat_data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@never_cache
@login_required
def atualizar_rat(request, rat_id):
    rat = get_object_or_404(Rat, id=rat_id)
    if request.method == 'POST':
        form = RatForm(request.POST, instance=rat)
        if form.is_valid():
            rat = form.save()
            # Limpa equipamentos antigos
            RatEquipamento.objects.filter(rat=rat).delete()
            # Salva equipamentos enviados
            equipamentos = zip(
                request.POST.getlist('equipamento[]'),
                request.POST.getlist('fabricante[]'),
                request.POST.getlist('modelo[]'),
                request.POST.getlist('numero_serie[]'),
                request.POST.getlist('data_instalacao[]'),
                request.POST.getlist('data_compra[]'),
            )
            for eq, fab, mod, num, data_inst, data_comp in equipamentos:
                if eq.strip():
                    RatEquipamento.objects.create(
                        rat=rat,
                        equipamento=eq,
                        fabricante=fab,
                        modelo=mod,
                        numero_serie=num,
                        data_instalacao=data_inst or None,
                        data_compra=data_comp or None,
                    )
            return redirect('rat:rat')
    return redirect('rat:rat')

@never_cache
@login_required
def excluir_rat(request, rat_id):
    rat = get_object_or_404(Rat, id=rat_id)
    if request.method == 'POST':
        rat.delete()
        return redirect('rat:rat')
    # Adicionar tratamento para GET ou outros métodos
    return redirect('rat:rat')

@never_cache
@login_required
def get_cliente_data(request, cliente_id):
    try:
        cliente = get_object_or_404(Clientes, id=cliente_id)
        cliente_data = {
            'success': True,
            'cliente': {
                'nome': cliente.nome,
                'telefone': cliente.telefone,
                'celular': cliente.celular,
                'email': cliente.email,
                'endereco': cliente.endereco,
                'bairro': cliente.bairro,
                'cidade': cliente.cidade,
                'cep': cliente.cep,
                'cpf_cnpj': cliente.cpf_cnpj,
            }
        }
        return JsonResponse(cliente_data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
