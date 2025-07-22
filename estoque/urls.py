from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    path('', views.estoque, name='estoque'),
    path('item/<int:item_id>/', views.get_item_details, name='get_item_details'),
    path('item/edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('item/delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('get/<int:estoque_id>/', views.get_estoque, name='get_estoque'),
    path('atualizar/<int:estoque_id>/', views.atualizar_estoque, name='atualizar_estoque'),
] 