from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    # Home
    path('', views.escola_home, name='escola_home'),
    
    # Itinerários Formativos
    path('itinerarios/', views.itinerario_list, name='itinerario_list'),
    path('itinerarios/novo/', views.itinerario_create, name='itinerario_create'),
    path('itinerarios/<int:pk>/', views.itinerario_detail, name='itinerario_detail'),
    path('itinerarios/<int:pk>/editar/', views.itinerario_edit, name='itinerario_edit'),
    
    # Unidades Curriculares
    path('unidades/', views.unidade_list, name='unidade_list'),
    path('unidades/nova/', views.unidade_create, name='unidade_create'),
    path('unidades/<int:pk>/', views.unidade_detail, name='unidade_detail'),
    
    # Enturmação
    path('itinerarios/<int:itinerario_pk>/enturmar/', views.enturmacao_create, name='enturmacao_create'),
    path('enturmacao/<int:pk>/remover/', views.enturmacao_delete, name='enturmacao_delete'),
]