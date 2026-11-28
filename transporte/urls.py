from django.urls import path
from . import views

app_name = 'transporte'

urlpatterns = [
    # Home e relatórios
    path('', views.transporte_home, name='transporte_home'),
    path('relatorio/', views.relatorio_transporte, name='relatorio_transporte'),

    # Motoristas
    path('motoristas/', views.motorista_list, name='motorista_list'),
    path('motoristas/novo/', views.motorista_create, name='motorista_create'),
    path('motoristas/<int:pk>/', views.motorista_detail, name='motorista_detail'),
    path('motoristas/<int:pk>/editar/', views.motorista_edit, name='motorista_edit'),
    path('motoristas/<int:pk>/excluir/', views.motorista_delete, name='motorista_delete'),

    # Veículos e manutenções
    path('veiculos/', views.veiculo_list, name='veiculo_list'),
    path('veiculos/novo/', views.veiculo_create, name='veiculo_create'),
    path('veiculos/<int:pk>/', views.veiculo_detail, name='veiculo_detail'),
    path('veiculos/<int:pk>/editar/', views.veiculo_edit, name='veiculo_edit'),
    path('veiculos/<int:veiculo_pk>/manutencao/nova/', views.manutencao_create, name='manutencao_create'),

    # Rotas e pontos de parada
    path('rotas/', views.rota_list, name='rota_list'),
    path('rotas/nova/', views.rota_create, name='rota_create'),
    path('rotas/<int:pk>/', views.rota_detail, name='rota_detail'),
    path('rotas/<int:pk>/editar/', views.rota_edit, name='rota_edit'),
    path('rotas/<int:rota_pk>/pontos/novo/', views.ponto_create, name='ponto_create'),
    path('pontos/<int:pk>/editar/', views.ponto_edit, name='ponto_edit'),

    # Alunos no transporte
    path('alunos/', views.aluno_transporte_list, name='aluno_transporte_list'),
    path('rotas/<int:rota_pk>/alunos/novo/', views.aluno_transporte_create, name='aluno_transporte_create'),
    path('alunos/<int:pk>/editar/', views.aluno_transporte_edit, name='aluno_transporte_edit'),

    # Viagens
    path('viagens/nova/', views.viagem_create, name='viagem_create'),

    # AJAX
    path('ajax/rotas/<int:rota_id>/pontos/', views.ajax_pontos_rota, name='ajax_pontos_rota'),
]
