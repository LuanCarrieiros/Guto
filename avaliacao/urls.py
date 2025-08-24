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
    
    # Disciplinas
    path('disciplinas/', views.disciplinas_list, name='disciplinas_list'),
    
    # Lançamento de Notas
    path('notas/', views.notas_list, name='notas_list'),
    path('notas/lancar/', views.lancar_notas, name='lancar_notas'),
    
    # Conceitos
    path('conceitos/', views.conceitos_list, name='conceitos_list'),
    
    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    
    # Diário Online
    path('diario/', views.diario_online, name='diario_online'),
]