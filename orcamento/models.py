from django.db import models
from decimal import Decimal
from clientes.models import Clientes

# Create your models here.

class Orcamento(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('aprovado', 'Aprovado'),
        ('cancelado', 'Cancelado'),
        ('finalizado', 'Finalizado'),
        ('pendente_pagamento', 'Pendente de Pagamento'),
        ('PAGO', 'PAGO'),
    ]

    cliente = models.ForeignKey(Clientes, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos')
    numero = models.CharField(max_length=20, unique=True)
    data = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, default='')
    endereco = models.CharField(max_length=255, blank=True, default='')
    cpf_cnpj = models.CharField(max_length=20, blank=True, default='')
    bairro = models.CharField(max_length=100, blank=True, default='')
    cidade = models.CharField(max_length=100, blank=True, default='')
    observacao = models.TextField(blank=True, default='')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    valor_total_com_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def save(self, *args, **kwargs):
        self.valor_total_com_desconto = self.valor_total - self.valor_desconto
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Orçamento {self.numero} - {self.nome}"

class ItemOrcamento(models.Model):
    orcamento = models.ForeignKey(Orcamento, related_name='itens', on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    produto = models.CharField(max_length=255)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produto} - {self.quantidade}x R$ {self.valor_unitario}"
