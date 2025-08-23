from django.urls import path
from . import views

app_name = 'censo'

urlpatterns = [
    # Home
    path('', views.censo_home, name='censo_home'),
    
    # Censo Escolar
    path('censo-escolar/', views.censo_escolar, name='censo_escolar'),
    path('censo-escolar/<int:ano>/', views.censo_escolar_ano, name='censo_escolar_ano'),
    
    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/matriculas/', views.relatorio_matriculas, name='relatorio_matriculas'),
    path('relatorios/funcionarios/', views.relatorio_funcionarios, name='relatorio_funcionarios'),
    path('relatorios/estatisticas/', views.relatorio_estatisticas, name='relatorio_estatisticas'),
    
    # Exportação
    path('exportar/<str:tipo>/', views.exportar_dados, name='exportar_dados'),
]