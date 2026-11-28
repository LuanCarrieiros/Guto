from django.urls import path
from . import views

app_name = 'funcionarios'

urlpatterns = [
    # Views principais de funcionários
    path('', views.funcionarios_home, name='funcionarios_home'),
    path('lista/', views.funcionario_list, name='funcionario_list'),
    path('create/', views.funcionario_create, name='funcionario_create'),
    path('buscar/', views.funcionario_busca_rede, name='funcionario_busca_rede'),
    path('imprimir/', views.funcionario_print, name='funcionario_print'),
    path('<int:pk>/', views.funcionario_detail, name='funcionario_detail'),
    path('<int:pk>/edit/', views.funcionario_edit, name='funcionario_edit'),
    path('<int:pk>/edit-extended/', views.funcionario_edit_extended, name='funcionario_edit_extended'),
    path('<int:pk>/delete/', views.funcionario_delete, name='funcionario_delete'),
    path('<int:pk>/arquivo/', views.funcionario_move_to_permanent, name='funcionario_move_to_permanent'),

    # Associação de professores e outros profissionais às turmas (RF501-RF511)
    path('associacoes/', views.associacao_professor_list, name='associacao_professor_list'),
    path('associacoes/professor/nova/', views.associacao_professor_create, name='associacao_professor_create'),
    path('associacoes/professor/<int:pk>/editar/', views.associacao_professor_edit, name='associacao_professor_edit'),
    path('associacoes/outros/nova/', views.associacao_outros_profissionais_create, name='associacao_outros_create'),
]