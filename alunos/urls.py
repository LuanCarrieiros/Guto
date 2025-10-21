from django.urls import path
from . import views

app_name = 'alunos'

urlpatterns = [
    # URLs para Alunos
    path('', views.alunos_home, name='alunos_home'),
    path('lista/', views.aluno_list, name='aluno_list'),
    path('cadastrar/', views.aluno_create, name='aluno_create'),
    path('<int:pk>/', views.aluno_detail, name='aluno_detail'),
    path('<int:pk>/editar/', views.aluno_edit, name='aluno_edit'),
    path('<int:pk>/editar-completo/', views.aluno_edit_extended, name='aluno_edit_extended'),
    path('<int:pk>/excluir/', views.aluno_delete, name='aluno_delete'),
    path('<int:pk>/mover-permanente/', views.aluno_move_to_permanent, name='aluno_move_to_permanent'),
    path('<int:pk>/imprimir/', views.aluno_print, name='aluno_print'),
    
    # URLs para Matrículas
    path('<int:aluno_pk>/matricula/nova/', views.matricula_create, name='matricula_create'),
    path('matricula/<int:pk>/editar/', views.matricula_edit, name='matricula_edit'),
    path('matricula/<int:pk>/excluir/', views.matricula_delete, name='matricula_delete'),
    path('matricula/<int:pk>/encerrar/', views.matricula_encerrar, name='matricula_encerrar'),
    path('matricula/<int:pk>/reativar/', views.matricula_reativar, name='matricula_reativar'),
]