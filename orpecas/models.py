from django.db import models
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class Orpecas(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('aprovado', 'Aprovado'),
        ('cancelado', 'Cancelado'),
        ('finalizado', 'Finalizado'),
        ('pendente_pagamento', 'Pendente de Pagamento'),
        ('PAGO', 'PAGO'),
    ]

    numero = models.CharField(max_length=50, unique=True, verbose_name="Nº Orçamento")
    data = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    
    # Informações do Cliente
    nome_cliente = models.CharField(max_length=255, verbose_name="Nome do Cliente")
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cpf_cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name="CPF/CNPJ")
    endereco = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    
    # Valores
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_total_com_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    observacao = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Orçamento Peças Nº {self.numero} - {self.nome_cliente}"

    class Meta:
        verbose_name = "Orçamento de Peça"
        verbose_name_plural = "Orçamentos de Peças"
        ordering = ['-data']

class ItemOrpecas(models.Model):
    orpecas = models.ForeignKey(Orpecas, related_name='itens', on_delete=models.CASCADE)
    produto = models.CharField(max_length=255)
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade} x {self.produto}"
    
    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario

def faturamento_orpecas_pagos(dias=30):
    data_inicio = timezone.now().date() - timedelta(days=dias)
    return Orpecas.objects.filter(
        status__iexact='PAGO',
        data__gte=data_inicio
    ).aggregate(total=Sum('valor_total_com_desconto'))['total'] or 0
