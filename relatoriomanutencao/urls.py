from django.urls import path
from . import views

app_name = 'relatoriomanutencao'

urlpatterns = [
    path('', views.RelatorioManutencaoCreateView.as_view(), name='relatoriomanutencao'),
    path('get-next-rat-number/', views.get_next_rat_number, name='get_next_rat_number'),
    path('api/rat/<int:pk>/', views.get_rat_details_json, name='get_rat_details_json'),
] 