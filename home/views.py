import json
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from orcamento.models import Orcamento
from clientes.models import Clientes
from django.utils import timezone
from django.http import HttpResponse
from agenda.models import Visita, AgendaDia
from orpecas.models import Orpecas
from rat.models import Rat
import calendar
from datetime import date

# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'home'

        # --- KPIs ---
        dias = int(self.request.GET.get('dias', 30))
        data_inicio = timezone.now().date() - timedelta(days=dias)

        # Faturamento OS
        os_faturamento = Clientes.objects.filter(
            status_servico__iexact='PAGO',
            data_chamado__gte=data_inicio
        ).aggregate(total=Sum('valor_total'))['total'] or 0

        # Faturamento Orçamentos
        orcamento_faturamento = Orcamento.objects.filter(
            status__iexact='PAGO',
            data__gte=data_inicio
        ).aggregate(total=Sum('valor_total_com_desconto'))['total'] or 0

        # Faturamento Orçamentos de Peças
        orpecas_faturamento = Orpecas.objects.filter(
            status__iexact='PAGO',
            data__gte=data_inicio
        ).aggregate(total=Sum('valor_total_com_desconto'))['total'] or 0

        faturamento_30d = os_faturamento + orcamento_faturamento + orpecas_faturamento

        # Dados para gráfico de pizza
        faturamento_pizza_data = json.dumps({
            'labels': ['OS', 'Orçamentos', 'Orçamentos de Peças'],
            'data': [float(os_faturamento), float(orcamento_faturamento), float(orpecas_faturamento)]
        })

        # Gráfico de linha: contagem de OS por mês nos últimos 12 meses
        hoje = timezone.now().date()
        meses = []
        os_por_mes = []
        for i in range(11, -1, -1):
            primeiro_dia = (hoje.replace(day=1) - timedelta(days=30*i)).replace(day=1)
            ano = primeiro_dia.year
            mes = primeiro_dia.month
            ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1])
            count = Clientes.objects.filter(
                data_chamado__gte=primeiro_dia,
                data_chamado__lte=ultimo_dia
            ).count()
            meses.append(f"{mes:02d}/{ano}")
            os_por_mes.append(count)
        os_por_mes_data = json.dumps({
            'labels': meses,
            'data': os_por_mes
        })

        # Total de OS/clientes cadastrados no período
        total_os_clientes = Clientes.objects.filter(data_chamado__gte=data_inicio).count()

        # OS abertas no período
        os_abertas = Clientes.objects.filter(data_chamado__gte=data_inicio).count()

        # OS finalizadas (status PAGO ou finalizado) no período
        os_finalizadas = Clientes.objects.filter(
            Q(status_servico__iexact='PAGO') | Q(status_servico__iexact='finalizado'),
            data_chamado__gte=data_inicio
        ).count()

        # Gráfico de linha: faturamento por mês nos últimos 12 meses
        hoje = timezone.now().date()
        meses_fat = []
        fat_por_mes = []
        for i in range(11, -1, -1):
            primeiro_dia = (hoje.replace(day=1) - timedelta(days=30*i)).replace(day=1)
            ano = primeiro_dia.year
            mes = primeiro_dia.month
            ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1])
            os_fat = Clientes.objects.filter(
                status_servico__iexact='PAGO',
                data_chamado__gte=primeiro_dia,
                data_chamado__lte=ultimo_dia
            ).aggregate(total=Sum('valor_total'))['total'] or 0
            orc_fat = Orcamento.objects.filter(
                status__iexact='PAGO',
                data__gte=primeiro_dia,
                data__lte=ultimo_dia
            ).aggregate(total=Sum('valor_total_com_desconto'))['total'] or 0
            orpecas_fat = Orpecas.objects.filter(
                status__iexact='PAGO',
                data__gte=primeiro_dia,
                data__lte=ultimo_dia
            ).aggregate(total=Sum('valor_total_com_desconto'))['total'] or 0
            fat_total = float(os_fat) + float(orc_fat) + float(orpecas_fat)
            meses_fat.append(f"{mes:02d}/{ano}")
            fat_por_mes.append(fat_total)
        faturamento_por_mes_data = json.dumps({
            'labels': meses_fat,
            'data': fat_por_mes
        })

        # Gráfico de RATs
        hoje = timezone.now().date()
        meses_rat = []
        rat_total_mes = []
        rat_finalizadas_mes = []
        rat_abertas_mes = []
        for i in range(11, -1, -1):
            primeiro_dia = (hoje.replace(day=1) - timedelta(days=30*i)).replace(day=1)
            ano = primeiro_dia.year
            mes = primeiro_dia.month
            ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1])
            total = Rat.objects.filter(
                data_visita__gte=primeiro_dia,
                data_visita__lte=ultimo_dia
            ).count()
            finalizadas = Rat.objects.filter(
                status__iexact='finalizado',
                data_visita__gte=primeiro_dia,
                data_visita__lte=ultimo_dia
            ).count()
            abertas = Rat.objects.filter(
                status__iexact='aberto',
                data_visita__gte=primeiro_dia,
                data_visita__lte=ultimo_dia
            ).count()
            meses_rat.append(f"{mes:02d}/{ano}")
            rat_total_mes.append(total)
            rat_finalizadas_mes.append(finalizadas)
            rat_abertas_mes.append(abertas)
        grafico_rat_data = json.dumps({
            'labels': meses_rat,
            'total': rat_total_mes,
            'finalizadas': rat_finalizadas_mes,
            'abertas': rat_abertas_mes
        })

        context.update({
            'faturamento_30d': faturamento_30d,
            'dias': dias,
            'total_os_clientes': total_os_clientes,
            'os_abertas': os_abertas,
            'os_finalizadas': os_finalizadas,
            'faturamento_pizza_data': faturamento_pizza_data,
            'os_por_mes_data': os_por_mes_data,
            'faturamento_por_mes_data': faturamento_por_mes_data,
            'grafico_rat_data': grafico_rat_data,
        })

        # --- Top 5 Clientes por Faturamento ---
        top_clientes = Clientes.objects.annotate(
            total_gasto=Sum(
                'orcamentos__valor_total_com_desconto',
                filter=Q(orcamentos__status__in=['aprovado', 'finalizado'])
            )
        ).filter(total_gasto__isnull=False).order_by('-total_gasto')[:5]
        
        context['top_clientes'] = top_clientes

        # --- Dados para Gráficos ---
        # Faturamento mensal (últimos 6 meses)
        faturamento_mensal_data = self.get_faturamento_mensal()
        context['faturamento_chart_data'] = json.dumps(faturamento_mensal_data)

        # Status de Orçamentos
        status_orcamentos_data = self.get_status_orcamentos()
        context['status_chart_data'] = json.dumps(status_orcamentos_data)

        # Projeção de Faturamento (Próximos 3 meses)
        projecao_faturamento_data = self.get_projecao_faturamento()
        context['projecao_chart_data'] = json.dumps(projecao_faturamento_data)

        return context

    def get_faturamento_mensal(self):
        six_months_ago = datetime.now() - timedelta(days=180)
        faturamento_mensal = Orcamento.objects.filter(
            status__in=['aprovado', 'finalizado'],
            data__gte=six_months_ago
        ).annotate(month=TruncMonth('data')) \
         .values('month') \
         .annotate(total=Sum('valor_total_com_desconto')) \
         .order_by('month')
        
        return self.prepare_chart_data(faturamento_mensal, 'total')

    def get_status_orcamentos(self):
        # Soma dos valores por status
        status_sums = Orcamento.objects.values('status').annotate(total=Sum('valor_total_com_desconto'))
        status_map = {
            'aberto': 'Abertos',
            'aprovado': 'Aprovados',
            'cancelado': 'Cancelados',
            'finalizado': 'Finalizados',
            'pendente_pagamento': 'Pendentes',
            'PAGO': 'Pagos',
        }
        labels = [status_map.get(s['status'], s['status']) for s in status_sums]
        data = [float(s['total'] or 0) for s in status_sums]
        return {'labels': labels, 'data': data}

    def prepare_chart_data(self, queryset, value_field):
        labels = []
        data = []
        months_data = {item['month'].strftime('%Y-%m-01'): item[value_field] for item in queryset}
        
        current_date = datetime.now()
        for i in range(5, -1, -1):
            month_date = current_date - timedelta(days=i*30)
            month_key = month_date.strftime('%Y-%m-01')
            month_label = month_date.strftime('%b/%y')
            
            labels.append(month_label)
            value = months_data.get(month_key, 0)
            data.append(float(value))
            
        return {'labels': labels, 'data': data}

    def get_projecao_faturamento(self):
        today = timezone.now().date()
        # Próximos 90 dias
        three_months_from_now = today + timedelta(days=90)
        
        # Filtra orçamentos aprovados com data futura
        projecao = Orcamento.objects.filter(
            status='aprovado',
            data__range=[today, three_months_from_now] 
        ).annotate(
            year=ExtractYear('data'),
            month=ExtractMonth('data')
        ).values('year', 'month') \
         .annotate(total=Sum('valor_total_com_desconto')) \
         .order_by('year', 'month')

        labels = []
        data = []
        # Formata os dados para o gráfico
        for item in projecao:
            # Cria um objeto de data para formatação
            month_date = datetime(item['year'], item['month'], 1)
            labels.append(month_date.strftime('%b/%y'))
            data.append(float(item['total']))
        
        return {'labels': labels, 'data': data}

def index(request):
    return render(request, 'index.html')






