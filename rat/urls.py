from django.urls import path
from .views import RatView, get_rat, atualizar_rat, excluir_rat, get_cliente_data

app_name = 'rat'

urlpatterns = [
    path('', RatView.as_view(), name='rat'),
    path('get/<int:rat_id>/', get_rat, name='get_rat'),
    path('atualizar/<int:rat_id>/', atualizar_rat, name='atualizar_rat'),
    path('excluir/<int:rat_id>/', excluir_rat, name='excluir_rat'),
    path('get-cliente-data/<int:cliente_id>/', get_cliente_data, name='get_cliente_data'),
] 