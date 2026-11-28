"""Configuração de URLs do projeto GUTO."""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import LoginLembrarView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Sistema de autenticação
    path('login/', LoginLembrarView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Dashboard principal
    path('', include('dashboard.urls')),
    
    # Módulos do sistema
    path('alunos/', include('alunos.urls')),
    path('funcionarios/', include('funcionarios.urls')),
    path('opcoes/', include('opcoes.urls')),
    path('aee/', include('aee.urls')),
    path('turmas/', include('turma.urls')),
    path('diario/', include('diario.urls')),
    path('utilitarios/', include('utilitarios.urls')),
    path('escola/', include('escola.urls')),
    path('transporte/', include('transporte.urls')),
    path('programa/', include('programa.urls')),
    path('censo/', include('censo.urls')),
]

# Configuração para servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
