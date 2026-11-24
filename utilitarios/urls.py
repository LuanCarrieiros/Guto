from django.urls import path
from . import views

app_name = 'utilitarios'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_utilitarios, name='dashboard'),

    # Gerenciamento de Usuários (RF1803-RF1807)
    path('usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),
    path('usuarios/novo/', views.criar_usuario, name='criar_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),

    # Grupos de Acesso e Permissões (RF2102)
    path('grupos/', views.gerenciar_grupos, name='gerenciar_grupos'),
    path('grupos/<int:grupo_id>/editar/', views.editar_grupo, name='editar_grupo'),

    # Instituições
    path('instituicoes/', views.instituicoes, name='instituicoes'),
    path('instituicoes/<int:pk>/editar/', views.editar_instituicao, name='editar_instituicao'),

    # Configurações do Sistema (RF1907)
    path('configuracoes/', views.configuracoes_sistema, name='configuracoes_sistema'),

    # Dados Adicionais (RF1901)
    path('dados-adicionais/', views.dados_adicionais, name='dados_adicionais'),

    # Auditoria (RF2002)
    path('auditoria/', views.auditoria, name='auditoria'),

    # Solicitações de Transferência (RF2003)
    path('transferencias/', views.solicitacoes_transferencia, name='solicitacoes_transferencia'),
    path('transferencias/<int:solicitacao_id>/processar/', views.processar_transferencia, name='processar_transferencia'),

    # Tipos de Avaliação (RF1904)
    path('tipos-avaliacao/', views.tipos_avaliacao, name='tipos_avaliacao'),

    # Bloqueios de Funcionalidade (RF2103)
    path('bloqueios/', views.bloqueios_funcionalidade, name='bloqueios_funcionalidade'),
    path('bloqueios/<int:pk>/alternar/', views.alternar_bloqueio, name='alternar_bloqueio'),
]
