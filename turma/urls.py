from django.urls import path
from . import views

app_name = 'turma'

urlpatterns = [
    # Dashboard principal da Avaliação
    path('', views.avaliacao_home, name='avaliacao_home'),
    
    # Turmas
    path('turmas/', views.turmas_list, name='turmas_list'),
    path('turmas/criar/', views.turma_create, name='turma_create'),
    path('turmas/<int:pk>/', views.turma_detail, name='turma_detail'),
    path('turmas/<int:pk>/editar/', views.turma_edit, name='turma_edit'),
    path('turmas/<int:pk>/excluir/', views.turma_delete, name='turma_delete'),
    path('turmas/<int:pk>/enturmar/', views.enturmar_alunos, name='enturmar_alunos'),
    path('turmas/<int:pk>/desenturmar/<int:aluno_id>/', views.desenturmar_aluno, name='desenturmar_aluno'),
    
    # Disciplinas
    path('disciplinas/', views.disciplinas_list, name='disciplinas_list'),
    path('disciplinas/criar/', views.disciplina_create, name='disciplina_create'),
    path('disciplinas/<int:pk>/editar/', views.disciplina_edit, name='disciplina_edit'),
    path('disciplinas/<int:pk>/excluir/', views.disciplina_delete, name='disciplina_delete'),
    
    # Lançamento de Notas e Avaliações  
    path('notas/', views.notas_list, name='notas_list'),
    path('notas/lancar/', views.lancar_notas, name='lancar_notas'),
    
    # NOTA: Espelho do Diário - Para visualização de coordenação
    path('avaliacoes/', views.avaliacoes_list, name='avaliacoes_list'),
    path('avaliacoes/criar/', views.avaliacao_create, name='avaliacao_create'),
    path('avaliacoes/<int:pk>/', views.avaliacao_detail, name='avaliacao_detail'),
    path('avaliacoes/<int:pk>/editar/', views.avaliacao_edit, name='avaliacao_edit'),
    path('avaliacoes/<int:pk>/excluir/', views.avaliacao_delete, name='avaliacao_delete'),
    
    
    # Conceitos
    path('conceitos/', views.conceitos_list, name='conceitos_list'),
    
    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    
    # Gerenciar disciplinas de uma turma específica
    path('turmas/<int:turma_id>/disciplinas/', views.gerenciar_disciplinas_turma, name='gerenciar_disciplinas_turma'),
    
    # Diário Eletrônico
    path('diario/', views.diario_dashboard, name='diario_dashboard'),
    path('diario/home/', views.diario_home, name='diario_home'),
    path('diario/turma/<int:turma_id>/', views.diario_turma, name='turma_diario'),
    path('turma/<int:turma_id>/fazer-chamada/', views.fazer_chamada, name='fazer_chamada'),
    path('turma/<int:turma_id>/lancar-notas/', views.lancar_notas_diario, name='lancar_notas_diario'),
    path('turma/<int:turma_id>/gerenciar-avaliacoes/', views.gerenciar_avaliacoes_diario, name='gerenciar_avaliacoes_diario'),
    path('turma/<int:turma_id>/visualizar-avaliacoes/', views.visualizar_avaliacoes_diario, name='visualizar_avaliacoes_diario'),
    path('avaliacoes/<int:avaliacao_id>/editar/', views.editar_avaliacao_diario, name='editar_avaliacao_diario'),
    path('avaliacoes/<int:avaliacao_id>/excluir/', views.excluir_avaliacao_diario, name='excluir_avaliacao_diario'),

    
    # AJAX Endpoints
    path('ajax/anos-series/', views.get_anos_series_por_tipo, name='get_anos_series_por_tipo'),
]