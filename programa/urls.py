from django.urls import path
from . import views

app_name = 'programa'

urlpatterns = [
    # Home
    path('', views.programa_home, name='programa_home'),
    
    # Programas Pedagógicos
    path('programas/', views.programa_list, name='programa_list'),
    path('programas/novo/', views.programa_create, name='programa_create'),
    path('programas/<int:pk>/', views.programa_detail, name='programa_detail'),
    path('programas/<int:pk>/editar/', views.programa_edit, name='programa_edit'),
    
    # Módulos
    path('modulos/', views.modulo_list, name='modulo_list'),
    path('modulos/novo/', views.modulo_create, name='modulo_create'),
    path('modulos/<int:pk>/', views.modulo_detail, name='modulo_detail'),
    
    # Participantes
    path('programas/<int:programa_pk>/participantes/', views.participante_list, name='participante_list'),
    path('programas/<int:programa_pk>/inscrever/', views.participante_create, name='participante_create'),
    
    # Aulas
    path('aulas/', views.aula_list, name='aula_list'),
    path('aulas/nova/', views.aula_create, name='aula_create'),
    path('aulas/<int:pk>/frequencia/', views.frequencia_aula, name='frequencia_aula'),
]