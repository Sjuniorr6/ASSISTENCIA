from django.contrib import admin
from .models import AgendaDia, Visita

class VisitaInline(admin.TabularInline):
    model = Visita
    extra = 1

@admin.register(AgendaDia)
class AgendaDiaAdmin(admin.ModelAdmin):
    list_display = ('data', 'dia_semana')
    inlines = [VisitaInline]

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('agenda', 'horario', 'servico', 'cliente', 'profissional')
    list_filter = ('profissional',)
    search_fields = ('servico', 'cliente', 'profissional')
