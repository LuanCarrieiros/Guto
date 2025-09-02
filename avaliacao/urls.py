from django.urls import path
from . import views

app_name = 'avaliacao'

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
    path('avaliacoes/', views.avaliacoes_list, name='avaliacoes_list'),
    path('avaliacoes/criar/', views.avaliacao_create, name='avaliacao_create'),
    path('avaliacoes/<int:pk>/editar/', views.avaliacao_edit, name='avaliacao_edit'),
    path('avaliacoes/<int:pk>/excluir/', views.avaliacao_delete, name='avaliacao_delete'),
    path('avaliacoes/<int:pk>/', views.avaliacao_detail, name='avaliacao_detail'),
    path('avaliacoes/<int:avaliacao_id>/lancar-notas/', views.lancar_notas_avaliacao, name='lancar_notas_avaliacao'),
    
    # Conceitos
    path('conceitos/', views.conceitos_list, name='conceitos_list'),
    
    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    
    # Diário Online
    path('diario/', views.diario_online, name='diario_online'),
    
    # Gerenciar disciplinas de uma turma específica
    path('turmas/<int:turma_id>/disciplinas/', views.gerenciar_disciplinas_turma, name='gerenciar_disciplinas_turma'),
    
    # Diário online específico para uma turma
    path('turmas/<int:turma_id>/diario/', views.diario_online_turma, name='diario_online_turma'),
    
    # Diário Eletrônico - Electronic Class Journal
    path('diario-dashboard/', views.diario_dashboard, name='diario_dashboard'),
    path('turmas/<int:turma_id>/diario-completo/', views.turma_diario, name='turma_diario'),
    path('aulas/registrar/', views.registrar_aula, name='registrar_aula'),
    path('turmas/<int:turma_id>/aulas/registrar/', views.registrar_aula, name='registrar_aula_turma'),
    path('aulas/<int:aula_id>/chamada/', views.fazer_chamada, name='fazer_chamada'),
    path('avaliacoes/criar/<int:turma_id>/', views.criar_avaliacao, name='criar_avaliacao_turma'),
    
    # Reports and Analytics
    path('relatorios/frequencia/', views.relatorio_frequencia, name='relatorio_frequencia'),
    path('relatorios/frequencia/turma/<int:turma_id>/', views.relatorio_frequencia, name='relatorio_frequencia_turma'),
    path('relatorios/frequencia/aluno/<int:aluno_id>/', views.relatorio_frequencia, name='relatorio_frequencia_aluno'),
    path('relatorios/desempenho/', views.relatorio_desempenho, name='relatorio_desempenho'),
    path('relatorios/boletim/<int:aluno_id>/', views.gerar_boletim, name='gerar_boletim'),
    
    # Bulk Operations
    path('avaliacoes/<int:avaliacao_id>/bulk-notes/', views.bulk_grade_entry, name='bulk_grade_entry'),
    path('turmas/<int:turma_id>/bulk-attendance/', views.bulk_attendance, name='bulk_attendance'),
]