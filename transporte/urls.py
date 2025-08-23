from django.urls import path
from . import views

app_name = 'transporte'

urlpatterns = [
    # Home
    path('', views.transporte_home, name='transporte_home'),
    
    # Motoristas
    path('motoristas/', views.motorista_list, name='motorista_list'),
    path('motoristas/novo/', views.motorista_create, name='motorista_create'),
    path('motoristas/<int:pk>/', views.motorista_detail, name='motorista_detail'),
    
    # Veículos
    path('veiculos/', views.veiculo_list, name='veiculo_list'),
    path('veiculos/novo/', views.veiculo_create, name='veiculo_create'),
    path('veiculos/<int:pk>/', views.veiculo_detail, name='veiculo_detail'),
    
    # Rotas
    path('rotas/', views.rota_list, name='rota_list'),
    path('rotas/nova/', views.rota_create, name='rota_create'),
    path('rotas/<int:pk>/', views.rota_detail, name='rota_detail'),
]