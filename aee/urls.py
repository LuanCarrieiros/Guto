from django.urls import path
from . import views

app_name = 'aee'

urlpatterns = [
    # Dashboard principal do AEE
    path('', views.aee_home, name='aee_home'),
    
    # Projetos Pedagógicos
    path('projetos/', views.projetos_list, name='projetos_list'),
    path('projetos/novo/', views.projeto_create, name='projeto_create'),
    path('projetos/<int:pk>/', views.projeto_detail, name='projeto_detail'),
    path('projetos/<int:pk>/editar/', views.projeto_edit, name='projeto_edit'),
    
    # Turmas AEE
    path('turmas/', views.turmas_list, name='turmas_list'),
    path('turmas/nova/', views.turma_create, name='turma_create'),
    path('turmas/<int:pk>/', views.turma_detail, name='turma_detail'),
    path('turmas/<int:pk>/editar/', views.turma_edit, name='turma_edit'),
    
    # Enturmações
    path('enturmacoes/', views.enturmacoes_list, name='enturmacoes_list'),
    path('enturmacoes/nova/', views.enturmacao_create, name='enturmacao_create'),
]