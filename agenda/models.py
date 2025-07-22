from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class AgendaDia(models.Model):
    data = models.DateField(unique=True)
    dia_semana = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.data} ({self.dia_semana})"

class Visita(models.Model):
    agenda = models.ForeignKey(AgendaDia, related_name='visitas', on_delete=models.CASCADE)
    horario = models.TimeField()
    servico = models.CharField(max_length=255)
    cliente = models.CharField(max_length=255)
    profissional = models.CharField(max_length=255)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.horario} - {self.servico} ({self.cliente})"
