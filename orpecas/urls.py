from django.urls import path
from .views import OrpecasView, get_orpecas, atualizar_orpecas, excluir_orpecas

app_name = 'orpecas'

urlpatterns = [
    path('', OrpecasView.as_view(), name='orpecas'),
    path('get/<int:orpecas_id>/', get_orpecas, name='get_orpecas'),
    path('atualizar/<int:orpecas_id>/', atualizar_orpecas, name='atualizar_orpecas'),
    path('excluir/<int:orpecas_id>/', excluir_orpecas, name='excluir_orpecas'),
] 