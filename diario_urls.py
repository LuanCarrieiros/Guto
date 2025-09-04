from django.urls import path
from avaliacao import views

app_name = 'diario'

urlpatterns = [
    # Diário Eletrônico - Home
    path('', views.diario_home, name='home'),
    path('turma/<int:turma_id>/', views.diario_turma, name='turma'),
    
    # Estrutura Hierárquica: /diario/disciplina/
    path('disciplina/chamada/turma/<int:turma_id>/', views.fazer_chamada, name='chamada'),
    path('disciplina/notas/turma/<int:turma_id>/', views.lancar_notas_diario, name='notas'),
    path('disciplina/avaliacoes/turma/<int:turma_id>/', views.gerenciar_avaliacoes_diario, name='avaliacoes'),
    path('disciplina/espelho/turma/<int:turma_id>/', views.visualizar_avaliacoes_diario, name='espelho'),
    
    # Gerenciamento de Avaliações
    path('disciplina/avaliacao/<int:avaliacao_id>/editar/', views.editar_avaliacao_diario, name='editar_avaliacao'),
    path('disciplina/avaliacao/<int:avaliacao_id>/excluir/', views.excluir_avaliacao_diario, name='excluir_avaliacao'),
    
]