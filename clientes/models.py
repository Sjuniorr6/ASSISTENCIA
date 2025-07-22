from django.db import models

# Create your models here.

class Clientes(models.Model):
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('pendente_pagamento', 'Pendente de Pagamento'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
        ('PAGO', 'PAGO'),
    ]

    nome = models.CharField(max_length=200, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    cpf_cnpj = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    apto_bloco = models.CharField(max_length=50, blank=True, null=True)

    # Campos da Ordem de Serviço
    numero_os = models.CharField(max_length=50, unique=True, blank=True, null=True)
    data_chamado = models.DateField(blank=True, null=True)
    revendedor = models.CharField(max_length=200, blank=True, null=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    forma_pagamento = models.CharField(max_length=50, blank=True, null=True)
    tecnicos = models.CharField(max_length=255, blank=True, null=True)
    periodo = models.CharField(max_length=100, blank=True, null=True)
    data_instalacao = models.DateField(blank=True, null=True)
    servicos = models.TextField(max_length=2000,blank=True, null=True)
    status_servico = models.CharField(max_length=50, blank=True, null=True, choices=STATUS_CHOICES, default='agendado')
    relatorios_servicos_prestados = models.TextField(max_length=2000,blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
