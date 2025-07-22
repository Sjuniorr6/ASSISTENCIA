from django.urls import path
from .views import HomeView, index

app_name = 'home'

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', HomeView.as_view(), name='home'),
]
