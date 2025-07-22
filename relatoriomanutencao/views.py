from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Max, Q
from datetime import date
import json
from .models import RelatorioManutencao

class RelatorioManutencaoCreateView(CreateView):
    model = RelatorioManutencao
    template_name = 'relatoriomanutencao.html'
    fields = '__all__'
    success_url = reverse_lazy('relatoriomanutencao:relatoriomanutencao')

    def get_initial(self):
        return {'status': 'aberto'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Inicia o queryset com todos os relatórios
        relatorios_queryset = RelatorioManutencao.objects.all()

        # Obtém os parâmetros de pesquisa da URL (GET)
        search_name = self.request.GET.get('search_name', '')
        search_rat = self.request.GET.get('search_rat', '')

        # Aplica os filtros case-insensitive se os termos de pesquisa existirem
        if search_name:
            relatorios_queryset = relatorios_queryset.filter(cliente__icontains=search_name)
        if search_rat:
            relatorios_queryset = relatorios_queryset.filter(numero_rat__icontains=search_rat)

        context['object_list'] = relatorios_queryset
        context['search_name'] = search_name
        context['search_rat'] = search_rat

        return context

def get_next_rat_number(request):
    today = date.today()
    current_year = today.year
    prefix = str(current_year)

    # Encontra o número sequencial máximo para o ano atual
    last_rat = RelatorioManutencao.objects.filter(numero_rat__startswith=prefix).aggregate(Max('numero_rat'))['numero_rat__max']

    next_sequential_number = 1
    if last_rat:
        try:
            sequential_part_str = last_rat[len(prefix):]
            if sequential_part_str.isdigit():
                sequential_part = int(sequential_part_str)
                next_sequential_number = sequential_part + 1
        except (ValueError, IndexError):
            pass

    new_rat_number = f"{prefix}{next_sequential_number:03d}"
    return JsonResponse({'numero_rat': new_rat_number})

def get_rat_details_json(request, pk):
    rat_instance = get_object_or_404(RelatorioManutencao, pk=pk)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            for field, value in data.items():
                if hasattr(rat_instance, field):
                    if field in ['data_instalacao', 'data_visita', 'data_compra'] and value == '':
                        setattr(rat_instance, field, None)
                    else:
                        setattr(rat_instance, field, value)
            rat_instance.save()
            return JsonResponse({'status': 'success', 'message': 'RAT atualizado com sucesso'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    data = {
        'pk': rat_instance.pk,
        'numero_rat': rat_instance.numero_rat,
        'status': rat_instance.status,
        'data_instalacao': rat_instance.data_instalacao.strftime('%Y-%m-%d') if rat_instance.data_instalacao else '',
        'data_visita': rat_instance.data_visita.strftime('%Y-%m-%d') if rat_instance.data_visita else '',
        'periodo': rat_instance.periodo,
        'horario': rat_instance.horario.strftime('%H:%M') if rat_instance.horario else '',
        'cliente': rat_instance.cliente,
        'cpf_cnpj': rat_instance.cpf_cnpj,
        'telefone1': rat_instance.telefone1,
        'telefone2': rat_instance.telefone2,
        'email': rat_instance.email,
        'rg_inscricao': rat_instance.rg_inscricao,
        'endereco': rat_instance.endereco,
        'bairro': rat_instance.bairro,
        'cidade': rat_instance.cidade,
        'uf': rat_instance.uf,
        'cep': rat_instance.cep,
        'loja_revendedora': rat_instance.loja_revendedora,
        'data_compra': rat_instance.data_compra.strftime('%Y-%m-%d') if rat_instance.data_compra else '',
        'equipamento': rat_instance.equipamento,
        'numero_serie': rat_instance.numero_serie,
        'codigo_produto': rat_instance.codigo_produto,
        'fabricante': rat_instance.fabricante,
        'modelo': rat_instance.modelo,
        'diametro_tubulacao': rat_instance.diametro_tubulacao,
        'voltagem': rat_instance.voltagem,
        'numero_nota_fiscal': rat_instance.numero_nota_fiscal,
        'tipo_gas': rat_instance.tipo_gas,
        'equipe_tecnica': rat_instance.equipe_tecnica,
        'relatorio_interno': rat_instance.relatorio_interno,
        'servico_executar': rat_instance.servico_executar,
        'tipo_servico': rat_instance.tipo_servico,
    }
    return JsonResponse(data) 