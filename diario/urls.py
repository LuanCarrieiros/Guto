from django.urls import path
from . import views

app_name = 'diario'

urlpatterns = [
    # Diário Eletrônico - Home
    path('', views.diario_home, name='home'),
    path('dashboard/', views.diario_dashboard, name='diario_dashboard'),
    path('turma/<int:turma_id>/', views.diario_turma, name='turma'),
]