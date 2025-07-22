from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # A URL principal agora aponta para a nova view unificada
    path('', views.clientes_view, name='clientes'), 
    
    # URL da API para buscar os dados de um cliente
    path('get_cliente/<int:cliente_id>/', views.get_cliente, name='get_cliente'),
    
    # URL da API para atualizar um cliente
    path('atualizar_cliente/<int:cliente_id>/', views.atualizar_cliente, name='atualizar_cliente'),
    
    # URL para carregar mais clientes via AJAX
    path('carregar-mais/', views.carregar_mais_clientes, name='carregar_mais_clientes'),
    
    # URL para salvar um novo cliente
    path('salvar/', views.salvar_cliente, name='salvar_cliente'),
]