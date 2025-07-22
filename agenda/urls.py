from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.agenda_home, name='home'),
    path('dia/<str:data>/', views.agenda_dia, name='agenda_dia'),
    path('agendar/', views.agendar_visita, name='agendar_visita'),
    path('relatorio/pdf/', views.relatorio_pdf, name='relatorio_pdf'),
] 