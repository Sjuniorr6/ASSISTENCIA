from django.db import models
from clientes.models import Clientes

class Rat(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    TIPO_SERVICO_CHOICES = [
        ('garantia', 'Garantia'),
        ('corretiva', 'Corretiva'),
        ('Instalação', 'Instalação'),
    ]

    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='rats',null=True, blank=True)
    numero_rat = models.CharField(max_length=50, unique=True, verbose_name="Número da RAT")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    
    data_visita = models.DateField(blank=True, null=True, verbose_name="Data da Visita")
    periodo = models.CharField(max_length=50, blank=True, null=True, verbose_name="Período")
    horario = models.CharField(max_length=50, blank=True, null=True, verbose_name="Horário")

    # Informações do Equipamento
    data_instalacao = models.DateField(blank=True, null=True, verbose_name="Data da Instalação")
    loja_revendedora = models.CharField(max_length=100, blank=True, null=True, verbose_name="Loja Revendedora")
    data_compra = models.DateField(blank=True, null=True, verbose_name="Data da Compra")
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    equipamento = models.CharField(max_length=100, blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Série")
    codigo_produto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Código do Produto")
    diametro_tubulacao = models.CharField(max_length=50, blank=True, null=True, verbose_name="Diâmetro da Tubulação")
    voltagem = models.CharField(max_length=50, blank=True, null=True)
    numero_nota_fiscal = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número da Nota Fiscal")
    tipo_gas = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo do Gás")
    
    # Informações do Serviço
    equipe_tecnica = models.CharField(max_length=200, blank=True, null=True, verbose_name="Equipe Técnica")
    tipo_servico = models.CharField(max_length=20, choices=TIPO_SERVICO_CHOICES, blank=True, null=True, verbose_name="Tipo de Serviço")
    relatorio_interno = models.TextField(blank=True, null=True, verbose_name="Relatório Interno de Atendimentos Executados")
    servico_a_executar = models.TextField(blank=True, null=True, verbose_name="Serviço a Executar")
    
    # Informações do Cliente (para preenchimento manual ou cópia do cadastro)
    cliente_nome = models.CharField(max_length=200, blank=True, null=True)
    cliente_cpf_cnpj = models.CharField(max_length=20, blank=True, null=True)
    cliente_telefone = models.CharField(max_length=20, blank=True, null=True)
    cliente_celular = models.CharField(max_length=20, blank=True, null=True)
    cliente_email = models.EmailField(blank=True, null=True)
    cliente_endereco = models.CharField(max_length=255, blank=True, null=True)
    cliente_bairro = models.CharField(max_length=100, blank=True, null=True)
    cliente_cidade = models.CharField(max_length=100, blank=True, null=True)
    cliente_cep = models.CharField(max_length=10, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RAT {self.numero_rat} - {self.cliente.nome}"

    class Meta:
        verbose_name = "RAT"
        verbose_name_plural = "RATs"
        ordering = ['-data_visita']

class RatEquipamento(models.Model):
    rat = models.ForeignKey(Rat, on_delete=models.CASCADE, related_name='equipamentos')
    equipamento = models.CharField(max_length=100)
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True)
    data_instalacao = models.DateField(blank=True, null=True)
    data_compra = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.equipamento} - {self.modelo or ''}"
