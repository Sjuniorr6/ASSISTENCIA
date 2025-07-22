from django.db import models
from django.utils import timezone

class Estoque(models.Model):
    STATUS_CHOICES = (
        ('disponivel', 'Disponível'),
        ('em_uso', 'Em Uso'),
        ('reservado', 'Reservado'),
    )

    nome_peca = models.CharField(max_length=100, verbose_name="Produto")
    codigo = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Código do produto")
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    fornecedor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fabricante")
    descricao = models.TextField(blank=True, null=True, verbose_name="Informações sobre a Peça")
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    preco_compra = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Preço de Compra")
    data_entrada = models.DateTimeField(default=timezone.now, verbose_name="Data de entrada")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel', verbose_name="Status")

    def __str__(self):
        return f"{self.nome_peca} ({self.codigo})"

    class Meta:
        verbose_name = "Item de Estoque"
        verbose_name_plural = "Itens de Estoque"
        ordering = ['-id']
