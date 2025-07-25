"""
URL configuration for tech project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('home/', include('home.urls', namespace='home')),
    path('home/', RedirectView.as_view(url='/', permanent=True)),
    path('clientes/', include('clientes.urls', namespace='clientes')),
    path('relatoriomanutencao/', include('relatoriomanutencao.urls')),
    path('orcamento/', include('orcamento.urls', namespace='orcamento')),
    path('rat/', include('rat.urls', namespace='rat')),
    path('orpecas/', include('orpecas.urls', namespace='orpecas')),
    path('pagpendentes/', include('pagpendentes.urls', namespace='pagpendentes')),
    path('agenda/', include('agenda.urls', namespace='agenda')),
    path('estoque/', include('estoque.urls')),
    path('accounts/', include('accounts.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(BASE_DIR, "static"))
