from django.urls import path
from avaliacao import views

app_name = 'diario'

urlpatterns = [
    # Diário Eletrônico
    path('', views.diario_home, name='home'),
    path('turma/<int:turma_id>/', views.diario_turma, name='turma'),
    path('turma/<int:turma_id>/chamada/', views.fazer_chamada, name='chamada'),
    path('turma/<int:turma_id>/notas/', views.lancar_notas_diario, name='notas'),
]