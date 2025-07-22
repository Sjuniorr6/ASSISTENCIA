from django.urls import path
from .views import PagamentosPendentesView, marcar_como_pago

app_name = 'pagpendentes'

urlpatterns = [
    path('', PagamentosPendentesView.as_view(), name='lista'),
    path('marcar-pago/', marcar_como_pago, name='marcar_pago'),
] 