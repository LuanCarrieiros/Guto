from django.urls import path
from . import views

app_name = 'funcionarios'

urlpatterns = [
    # Views principais de funcionários
    path('', views.funcionario_list, name='funcionario_list'),
    path('create/', views.funcionario_create, name='funcionario_create'),
    path('<int:codigo>/', views.funcionario_detail, name='funcionario_detail'),
    path('<int:codigo>/edit/', views.funcionario_edit, name='funcionario_edit'),
    path('<int:codigo>/edit-extended/', views.funcionario_edit_extended, name='funcionario_edit_extended'),
    path('<int:codigo>/delete/', views.funcionario_delete, name='funcionario_delete'),
]