from django.test import TestCase
from django.urls import reverse

from guto_system.testing import criar_admin, criar_aluno
from .models import EnturmacaoAEE, HistoricoEnturmacao, ProjetoPedagogico, TurmaAEE


class AEEFluxoTest(TestCase):
    def setUp(self):
        self.user = criar_admin()
        self.client.force_login(self.user)
        self.aluno = criar_aluno(self.user)

    def test_fluxo_projeto_turma_enturmacao(self):
        resp = self.client.post(reverse('aee:projeto_create'), {
            'nome': 'Sala de Recursos', 'tipo_projeto': 'AEE', 'periodo_letivo': '2026',
            'carga_horaria': 10, 'descricao': '', 'ativo': 'on',
        })
        projeto = ProjetoPedagogico.objects.get()
        self.assertRedirects(resp, reverse('aee:projeto_detail', args=[projeto.pk]))

        resp = self.client.post(reverse('aee:turma_create'), {
            'nome': 'AEE Manhã', 'projeto_pedagogico': projeto.pk, 'periodo_letivo': '2026',
            'turno': 'MATUTINO', 'hora_inicio': '08:00', 'hora_fim': '10:00', 'maximo_alunos': 1,
            'ordenacao': 'ALFABETICA', 'segunda': 'on', 'situacao': 'ATIVO',
        })
        turma = TurmaAEE.objects.get()
        self.assertRedirects(resp, reverse('aee:turma_detail', args=[turma.pk]))

        dados = {'turma': turma.pk, 'aluno': self.aluno.pk, 'origem': 'PROPRIA_ESCOLA',
                 'ano_administrativo': '2026', 'tipo_ensino': 'Fundamental', 'ano_serie': '5º ano'}
        self.client.post(reverse('aee:enturmacao_create'), dados)
        self.assertEqual(EnturmacaoAEE.objects.filter(ativo=True).count(), 1)

        # Turma lotada: segunda enturmação é recusada
        outro = criar_aluno(self.user, nome='Outro Aluno')
        resp = self.client.post(reverse('aee:enturmacao_create'), {**dados, 'aluno': outro.pk})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(EnturmacaoAEE.objects.filter(ativo=True).count(), 1)

        # Remoção mantém histórico e permite nova enturmação depois
        enturmacao = EnturmacaoAEE.objects.get(ativo=True)
        self.client.post(reverse('aee:enturmacao_remover', args=[enturmacao.pk]))
        self.assertFalse(EnturmacaoAEE.objects.filter(ativo=True).exists())
        self.assertEqual(HistoricoEnturmacao.objects.count(), 2)
        self.client.post(reverse('aee:enturmacao_create'), dados)
        self.assertEqual(EnturmacaoAEE.objects.filter(ativo=True).count(), 1)

        for nome in ('aee:aee_home', 'aee:projetos_list', 'aee:turmas_list', 'aee:enturmacoes_list'):
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200)
        self.assertEqual(self.client.get(reverse('aee:turma_detail', args=[turma.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('aee:projeto_edit', args=[projeto.pk])).status_code, 200)

    def test_turma_exige_dia_da_semana_e_horario_valido(self):
        projeto = ProjetoPedagogico.objects.create(nome='P', tipo_projeto='AC', usuario_criacao=self.user)
        resp = self.client.post(reverse('aee:turma_create'), {
            'nome': 'T', 'projeto_pedagogico': projeto.pk, 'periodo_letivo': '2026', 'turno': 'MATUTINO',
            'hora_inicio': '10:00', 'hora_fim': '09:00', 'maximo_alunos': 10, 'ordenacao': 'ALFABETICA',
            'situacao': 'ATIVO',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(TurmaAEE.objects.exists())
