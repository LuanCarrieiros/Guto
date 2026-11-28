from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from guto_system.testing import criar_admin, criar_aluno
from .models import BloqueioFuncionalidade, GrupoAcesso, Instituicao, PermissaoGrupo, RegistroAuditoria, SolicitacaoTransferencia


class UtilitariosPaginasTest(TestCase):
    def setUp(self):
        self.admin = criar_admin()
        self.client.force_login(self.admin)

    def test_paginas_abrem(self):
        nomes = ['dashboard', 'gerenciar_usuarios', 'criar_usuario', 'gerenciar_grupos', 'instituicoes',
                 'configuracoes_sistema', 'dados_adicionais', 'auditoria', 'solicitacoes_transferencia',
                 'tipos_avaliacao', 'bloqueios_funcionalidade']
        for nome in nomes:
            self.assertEqual(self.client.get(reverse(f'utilitarios:{nome}')).status_code, 200, nome)
        self.assertEqual(self.client.get(reverse('utilitarios:editar_usuario', args=[self.admin.pk])).status_code, 200)

    def test_usuario_comum_nao_acessa_utilitarios(self):
        comum = User.objects.create_user('comum', password='senha-forte-123')
        self.client.force_login(comum)
        resp = self.client.get(reverse('utilitarios:dashboard'))
        self.assertEqual(resp.status_code, 302)

    def test_criar_usuario_com_grupo(self):
        grupo = GrupoAcesso.objects.create(nome='Professor', usuario_criacao=self.admin)
        self.client.post(reverse('utilitarios:criar_usuario'), {
            'username': 'prof1', 'first_name': 'Ana', 'last_name': 'Silva', 'email': 'ana@example.com',
            'is_active': 'on', 'nova_senha': 'Senha-Muito-Forte-42', 'grupos': [grupo.pk],
        })
        usuario = User.objects.get(username='prof1')
        self.assertTrue(usuario.check_password('Senha-Muito-Forte-42'))
        self.assertEqual(list(usuario.groups.values_list('name', flat=True)), ['Professor'])

    def test_transferencia_aceita(self):
        origem = Instituicao.objects.create(nome='Escola A', codigo='A', tipo_instituicao='ESCOLA')
        destino = Instituicao.objects.create(nome='Escola B', codigo='B', tipo_instituicao='ESCOLA')
        aluno = criar_aluno(self.admin)
        self.client.post(reverse('utilitarios:solicitacoes_transferencia'), {
            'aluno': aluno.pk, 'escola_origem': origem.pk, 'escola_destino': destino.pk, 'motivo': 'Mudança',
        })
        solicitacao = SolicitacaoTransferencia.objects.get()
        self.client.post(reverse('utilitarios:processar_transferencia', args=[solicitacao.pk]), {'acao': 'aceitar'})
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, 'ACEITA')
        self.assertEqual(solicitacao.usuario_processamento, self.admin)


class ControleAcessoTest(TestCase):
    """Bloqueios e permissões configurados em Utilitários são aplicados nos módulos."""

    def setUp(self):
        self.admin = criar_admin()
        self.usuario = User.objects.create_user('secretaria', password='senha-forte-123')
        self.client.force_login(self.usuario)

    def test_bloqueio_impede_inclusao(self):
        BloqueioFuncionalidade.objects.create(
            modulo='escola', funcionalidade='INCLUIR', tipo_bloqueio='DIRETO', motivo='Fechamento do ano',
            data_inicio=timezone.now() - timedelta(hours=1), usuario_criacao=self.admin,
        )
        # Visualizar continua permitido
        self.assertEqual(self.client.get(reverse('escola:itinerario_create')).status_code, 200)
        resp = self.client.post(reverse('escola:itinerario_create'), {
            'nome': 'X', 'carga_horaria_total': 10, 'areas_conhecimento': 'MATEMATICA', 'habilidades': 'h',
            'vagas_disponiveis': 5,
        })
        self.assertEqual(resp.status_code, 302)
        from escola.models import ItinerarioFormativo
        self.assertFalse(ItinerarioFormativo.objects.exists())

    def test_permissao_de_grupo_bloqueia_visualizacao(self):
        grupo = GrupoAcesso.objects.create(nome='Portaria', usuario_criacao=self.admin)
        PermissaoGrupo.objects.create(grupo=grupo, modulo='transporte', visualizar=False)
        from django.contrib.auth.models import Group
        self.usuario.groups.add(Group.objects.create(name='Portaria'))
        self.assertEqual(self.client.get(reverse('transporte:transporte_home')).status_code, 403)
        self.assertEqual(self.client.get(reverse('escola:escola_home')).status_code, 200)

    def test_auditoria_registra_login_e_alteracoes(self):
        self.client.logout()
        self.client.post(reverse('login'), {'username': 'secretaria', 'password': 'senha-forte-123'})
        self.assertTrue(RegistroAuditoria.objects.filter(usuario=self.usuario, acao='LOGIN').exists())
        self.client.post(reverse('escola:unidade_create'), {
            'nome': 'U', 'carga_horaria': 10, 'ementa': 'e', 'habilidades_especificas': 'h',
        })
        self.assertTrue(RegistroAuditoria.objects.filter(usuario=self.usuario, acao='CREATE', tela='escola').exists())
