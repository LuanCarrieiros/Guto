"""
URL configuration for guto_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def redirect_to_dashboard(request):
    """Redireciona login bem-sucedido para dashboard"""
    return redirect('dashboard:home')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Sistema de autenticação
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='accounts_login'),
    
    # Dashboard principal
    path('', include('dashboard.urls')),
    
    # Módulos do sistema
    path('alunos/', include('alunos.urls')),
    path('funcionarios/', include('funcionarios.urls')),
    path('opcoes/', include('opcoes.urls')),
    path('aee/', include('aee.urls')),
    path('avaliacao/', include('avaliacao.urls')),
    path('utilitarios/', include('utilitarios.urls')),
    path('escola/', include('escola.urls')),
    path('transporte/', include('transporte.urls')),
    path('programa/', include('programa.urls')),
    path('censo/', include('censo.urls')),
]

# Configuração para servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
