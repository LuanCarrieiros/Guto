from django.urls import path
from . import views

app_name = 'diario'

PERIODO = 'turma/<int:turma_id>/disciplina/<int:disciplina_id>/divisao/<int:divisao_id>/'

urlpatterns = [
    path('', views.diario_home, name='home'),

    # Navegação: Turma → Disciplina → Período
    path('turma/<int:turma_id>/', views.diario_turma, name='turma'),
    path('turma/<int:turma_id>/disciplina/<int:disciplina_id>/', views.diario_disciplina, name='disciplina'),
    path(PERIODO, views.diario_divisao, name='divisao'),

    # Ações do período
    path(PERIODO + 'chamada/', views.fazer_chamada, name='chamada'),
    path(PERIODO + 'notas/', views.lancar_notas, name='lancar_notas'),
    path(PERIODO + 'avaliacoes/', views.gerenciar_avaliacoes, name='gerenciar_avaliacoes'),
    path(PERIODO + 'avaliacoes/espelho/', views.visualizar_avaliacoes, name='visualizar_avaliacoes'),
    path(PERIODO + 'pareceres/', views.pareceres, name='pareceres'),
    path('avaliacoes/<int:avaliacao_id>/editar/', views.editar_avaliacao, name='editar_avaliacao'),
    path('avaliacoes/<int:avaliacao_id>/excluir/', views.excluir_avaliacao, name='excluir_avaliacao'),

    # Ações da disciplina (ano todo)
    path('turma/<int:turma_id>/disciplina/<int:disciplina_id>/recuperacao/', views.recuperacao, name='recuperacao'),
    path('turma/<int:turma_id>/disciplina/<int:disciplina_id>/fechar/', views.fechar_diario, name='fechar_diario'),
    path('turma/<int:turma_id>/disciplina/<int:disciplina_id>/abrir/', views.abrir_diario, name='abrir_diario'),
]
