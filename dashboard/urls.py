from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('estatisticas/', views.estatisticas, name='estatisticas'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    path('em-desenvolvimento/', views.em_desenvolvimento, name='em_desenvolvimento'),
]