from django.urls import path
from . import views

app_name = 'diario'

urlpatterns = [
    # Diário Eletrônico - Home e Dashboard
    path('', views.diario_home, name='home'),
    path('dashboard/', views.diario_dashboard, name='diario_dashboard'),

    # Processo em 3 etapas: Turma → Disciplina → Divisão
    path('turma/<int:turma_id>/', views.diario_turma, name='turma'),
    path('turma/<int:turma_id>/disciplina/<int:disciplina_id>/', views.diario_disciplina, name='disciplina'),
    path('turma/<int:turma_id>/disciplina/<int:disciplina_id>/divisao/<int:divisao_id>/', views.diario_divisao, name='divisao'),

    # Controle de diário (fechar/abrir)
    path('turma/<int:turma_id>/disciplina/<int:disciplina_id>/fechar/', views.fechar_diario, name='fechar_diario'),
    path('turma/<int:turma_id>/disciplina/<int:disciplina_id>/abrir/', views.abrir_diario, name='abrir_diario'),

    # Gerenciar avaliações via diário
    path('disciplina/avaliacoes/turma/<int:turma_id>/', views.gerenciar_avaliacoes_via_diario, name='gerenciar_avaliacoes_via_diario'),
]