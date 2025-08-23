from django.urls import path
from . import views

app_name = 'opcoes'

urlpatterns = [
    # URLs principais do módulo Opções (RF601-RF602)
    path('', views.opcoes_home, name='opcoes_home'),
    
    # URLs para Documentos/Relatórios (RF603-RF607)
    path('documentos/', views.documentos_home, name='documentos_home'),
    path('documentos/<int:tipo_relatorio_id>/', views.selecionar_relatorio, name='selecionar_relatorio'),
    path('relatorio/<int:filtro_id>/', views.gerar_relatorio, name='gerar_relatorio'),
    
    # URLs para Calendário Escolar (RF701-RF704)
    path('calendario/', views.calendario_escolar, name='calendario_escolar'),
    path('calendario/criar/', views.calendario_criar, name='calendario_criar'),
    path('calendario/<int:pk>/editar/', views.calendario_editar, name='calendario_editar'),
    path('calendario/<int:pk>/', views.calendario_detalhe, name='calendario_detalhe'),
    path('calendario/<int:calendario_id>/evento/criar/', views.evento_criar, name='evento_criar'),
]