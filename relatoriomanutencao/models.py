from django.db import models

class RelatorioManutencao(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('finalizado', 'Finalizado'),
    ]

    TIPO_SERVICO_CHOICES = [
        ('instalacao', 'Instalação'),
        ('garantia', 'Garantia'),
        ('corretiva', 'Corretiva'),
    ]

    # Campos de identificação
    numero_rat = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    
    # Datas e períodos
    data_instalacao = models.DateField(null=True, blank=True)
    data_visita = models.DateField(null=True, blank=True)
    periodo = models.CharField(max_length=100, blank=True, null=True)
    horario = models.TimeField(null=True, blank=True)
    
    # Informações do cliente
    cliente = models.CharField(max_length=200)
    cpf_cnpj = models.CharField(max_length=20, blank=True, null=True)
    telefone1 = models.CharField(max_length=20, blank=True, null=True)
    telefone2 = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    rg_inscricao = models.CharField(max_length=50, blank=True, null=True)
    
    # Endereço
    endereco = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    
    # Informações do equipamento
    loja_revendedora = models.CharField(max_length=200, blank=True, null=True)
    data_compra = models.DateField(null=True, blank=True)
    equipamento = models.CharField(max_length=200, blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True)
    codigo_produto = models.CharField(max_length=100, blank=True, null=True)
    fabricante = models.CharField(max_length=200, blank=True, null=True)
    modelo = models.CharField(max_length=200, blank=True, null=True)
    diametro_tubulacao = models.CharField(max_length=50, blank=True, null=True)
    
    # Informações técnicas
    voltagem = models.CharField(max_length=50, blank=True, null=True)
    numero_nota_fiscal = models.CharField(max_length=100, blank=True, null=True)
    tipo_gas = models.CharField(max_length=100, blank=True, null=True)
    equipe_tecnica = models.CharField(max_length=200, blank=True, null=True)
    
    # Relatórios
    relatorio_interno = models.TextField(blank=True, null=True)
    servico_executar = models.TextField(blank=True, null=True)
    
    # Tipo de serviço
    tipo_servico = models.CharField(
        max_length=20,
        choices=TIPO_SERVICO_CHOICES,
        default='instalacao'
    )
    
    # Campos de controle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RAT {self.numero_rat} - {self.cliente}"

    class Meta:
        verbose_name = 'Relatório de Manutenção'
        verbose_name_plural = 'Relatórios de Manutenção'
        ordering = ['-created_at'] 