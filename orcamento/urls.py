from django.urls import path
from . import views

app_name = 'orcamento'

urlpatterns = [
    path('', views.lista_orcamentos, name='lista_orcamentos'),
    path('get_orcamento/<int:id>/', views.get_orcamento, name='get_orcamento'),
    path('salvar/', views.salvar_orcamento, name='salvar_orcamento'),
    path('novo/', views.novo_orcamento, name='novo_orcamento'),
    path('<int:id>/atualizar/', views.atualizar_orcamento, name='atualizar_orcamento'),
    path('<int:orcamento_id>/', views.detalhe_orcamento, name='detalhe_orcamento'),
] 