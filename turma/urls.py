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
    
    
    # Conceitos
    path('conceitos/', views.conceitos_list, name='conceitos_list'),
    
    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    
    # Gerenciar disciplinas de uma turma específica
    path('turmas/<int:turma_id>/disciplinas/', views.gerenciar_disciplinas_turma, name='gerenciar_disciplinas_turma'),
    
    # Diário Eletrônico
    path('diario/', views.diario_dashboard, name='diario_dashboard'),
    
    # AJAX Endpoints
    path('ajax/anos-series/', views.get_anos_series_por_tipo, name='get_anos_series_por_tipo'),
]