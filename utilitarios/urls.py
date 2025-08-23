from django.urls import path
from . import views

app_name = 'utilitarios'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_utilitarios, name='dashboard'),
    
    # Gerenciamento de Usuários (RF1803-RF1807)
    path('usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    
    # Gerenciamento de Grupos de Acesso
    path('grupos/', views.gerenciar_grupos, name='gerenciar_grupos'),
    path('grupos/<int:grupo_id>/editar/', views.editar_grupo, name='editar_grupo'),
    
    # Configurações do Sistema
    path('configuracoes/', views.configuracoes_sistema, name='configuracoes_sistema'),
    
    # Dados Adicionais
    path('dados-adicionais/', views.dados_adicionais, name='dados_adicionais'),
    
    # Auditoria
    path('auditoria/', views.auditoria, name='auditoria'),
    
    # Solicitações de Transferência
    path('transferencias/', views.solicitacoes_transferencia, name='solicitacoes_transferencia'),
    path('transferencias/<int:solicitacao_id>/processar/', views.processar_transferencia, name='processar_transferencia'),
    
    # Tipos de Avaliação
    path('tipos-avaliacao/', views.tipos_avaliacao, name='tipos_avaliacao'),
    
    # Bloqueios de Funcionalidade
    path('bloqueios/', views.bloqueios_funcionalidade, name='bloqueios_funcionalidade'),
]