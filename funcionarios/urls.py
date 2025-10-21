from django.urls import path
from . import views

app_name = 'funcionarios'

urlpatterns = [
    # Views principais de funcionários
    path('', views.funcionarios_home, name='funcionarios_home'),
    path('lista/', views.funcionario_list, name='funcionario_list'),
    path('create/', views.funcionario_create, name='funcionario_create'),
    path('<int:pk>/', views.funcionario_detail, name='funcionario_detail'),
    path('<int:pk>/edit/', views.funcionario_edit, name='funcionario_edit'),
    path('<int:pk>/edit-extended/', views.funcionario_edit_extended, name='funcionario_edit_extended'),
    path('<int:pk>/delete/', views.funcionario_delete, name='funcionario_delete'),
]