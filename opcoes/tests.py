from datetime import date

from django.test import TestCase
from django.urls import reverse

from guto_system.testing import criar_admin, criar_aluno, criar_turma
from turma.models import Enturmacao
from .models import CalendarioEscolar, EventoCalendario, FiltroRelatorio, TipoRelatorio


class CalendarioTest(TestCase):
    def setUp(self):
        self.user = criar_admin()
        self.client.force_login(self.user)

    def test_calendario_com_eventos_e_impressao(self):
        ano = date.today().year
        self.client.post(reverse('opcoes:calendario_criar'), {
            'periodo_letivo': str(ano), 'tipo_ensino': 'FUNDAMENTAL_I', 'serie': '5_ANO', 'turno': 'MATUTINO',
            'data_inicio_letivo': f'{ano}-02-01', 'data_fim_letivo': f'{ano}-12-15',
            'dias_letivos': 200, 'dias_escolares': 200, 'ativo': 'on',
        })
        calendario = CalendarioEscolar.objects.get()
        self.client.post(reverse('opcoes:evento_criar', args=[calendario.pk]), {
            'data_evento': f'{ano}-09-07', 'tipo_evento': 'FERIADO', 'nome_evento': 'Independência',
        })
        self.assertEqual(EventoCalendario.objects.count(), 1)

        resp = self.client.get(reverse('opcoes:calendario_escolar'))
        self.assertContains(resp, 'Independência')
        self.assertEqual(len(resp.context['meses']), 12)
        self.assertContains(self.client.get(reverse('opcoes:calendario_escolar') + '?format=print'), 'Setembro')
        self.assertEqual(self.client.get(reverse('opcoes:calendario_detalhe', args=[calendario.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('opcoes:calendario_editar', args=[calendario.pk])).status_code, 200)


class RelatorioTest(TestCase):
    def setUp(self):
        self.user = criar_admin()
        self.client.force_login(self.user)

    def test_relatorio_usa_turmas_reais(self):
        turma = criar_turma(self.user)
        criar_turma(self.user, nome='Turma Tarde').__class__.objects.filter(nome='Turma Tarde').update(turno='VESPERTINO')
        aluno = criar_aluno(self.user)
        Enturmacao.objects.create(turma=turma, aluno=aluno, usuario_enturmacao=self.user)

        self.client.get(reverse('opcoes:documentos_home'))
        tipo = TipoRelatorio.objects.get(nome='BOLETIM')
        self.client.post(reverse('opcoes:selecionar_relatorio', args=[tipo.pk]), {
            'periodo_letivo': turma.periodo_letivo, 'tipo_ensino': 'FUNDAMENTAL_I', 'turno': 'MATUTINO',
            'status_diario': 'TODOS', 'situacao_turma': 'TODOS',
        })
        filtro = FiltroRelatorio.objects.get()
        resp = self.client.get(reverse('opcoes:gerar_relatorio', args=[filtro.pk]))
        self.assertEqual(resp.context['total_turmas'], 1)
        self.assertEqual(resp.context['total_alunos'], 1)
        self.assertContains(resp, aluno.nome)
        self.assertEqual(self.client.get(reverse('opcoes:gerar_relatorio', args=[filtro.pk]) + '?format=print').status_code, 200)
