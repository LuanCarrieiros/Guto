"""
Integridade dos vínculos entre alunos, turmas, disciplinas e professores.

Cobre as situações que mais causam confusão: alunos com o mesmo nome em turmas
diferentes, várias turmas da mesma disciplina com professores diferentes,
transferências sucessivas e disciplinas cadastradas em duplicidade.
"""
import json
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from funcionarios.forms import AssociacaoProfessorForm
from funcionarios.models import AssociacaoProfessor
from guto_system.testing import criar_admin, criar_aluno, criar_funcionario, criar_turma
from turma.forms import DisciplinaForm
from turma.models import Avaliacao, Disciplina, DivisaoPeriodoLetivo, Enturmacao, NotaAvaliacao, TipoAvaliacao


class Base(TestCase):
    def setUp(self):
        self.admin = criar_admin()
        self.ano = date.today().year
        self.turma_a = criar_turma(self.admin, nome='1º A')
        self.turma_b = criar_turma(self.admin, nome='1º B')
        self.matematica = Disciplina.objects.create(nome='Matemática', codigo='MAT')
        self.divisao = DivisaoPeriodoLetivo.objects.create(
            nome='1º Bimestre', tipo_divisao='BIMESTRE', periodo_letivo=str(self.ano), ordem=1,
            data_inicio=date(self.ano, 1, 1), data_fim=date(self.ano, 12, 31),
        )
        self.tipo = TipoAvaliacao.objects.create(nome='Prova')

    def avaliacao(self, turma):
        return Avaliacao.objects.create(
            turma=turma, disciplina=self.matematica, divisao_periodo=self.divisao, tipo_avaliacao=self.tipo,
            professor=self.admin, nome='Prova 1', data_aplicacao=date.today(),
        )

    def associar(self, professor, turma, disciplina=None, inicio=None, termino=None, tipo='DISCIPLINA'):
        return AssociacaoProfessor.objects.create(
            funcionario=professor, turma=turma, disciplina=disciplina or self.matematica, tipo_associacao=tipo,
            data_inicio=inicio or date(self.ano, 1, 1), data_termino=termino, usuario_cadastro=self.admin,
        )


class AlunosHomonimosTest(Base):
    def test_alunos_com_mesmo_nome_em_turmas_diferentes_nao_se_misturam(self):
        """O "Aluno 1" de Matemática do 1º A não sobrescreve o "Aluno 1" do 1º B."""
        aluno_a = criar_aluno(self.admin, nome='João da Silva')
        aluno_b = criar_aluno(self.admin, nome='João da Silva')
        Enturmacao.enturmar(self.turma_a, aluno_a, self.admin)
        Enturmacao.enturmar(self.turma_b, aluno_b, self.admin)
        prova_a, prova_b = self.avaliacao(self.turma_a), self.avaliacao(self.turma_b)

        self.client.force_login(self.admin)
        for turma, prova, aluno, nota in ((self.turma_a, prova_a, aluno_a, '9'), (self.turma_b, prova_b, aluno_b, '4')):
            url = reverse('diario:lancar_notas', args=[turma.pk, self.matematica.pk, self.divisao.pk])
            resposta = self.client.post(url, json.dumps({'aluno_id': aluno.pk, 'avaliacao_id': prova.pk, 'nota': nota}),
                                        content_type='application/json')
            self.assertTrue(resposta.json()['success'])

        self.assertEqual(float(NotaAvaliacao.objects.get(aluno=aluno_a).nota), 9.0)
        self.assertEqual(float(NotaAvaliacao.objects.get(aluno=aluno_b).nota), 4.0)

        # Lançar nota de um aluno numa avaliação de outra turma é recusado
        url = reverse('diario:lancar_notas', args=[self.turma_a.pk, self.matematica.pk, self.divisao.pk])
        resposta = self.client.post(url, json.dumps({'aluno_id': aluno_b.pk, 'avaliacao_id': prova_a.pk, 'nota': '1'}),
                                    content_type='application/json')
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(NotaAvaliacao.objects.count(), 2)


class EnturmacaoHistoricoTest(Base):
    def test_transferencias_sucessivas_preservam_historico(self):
        turma_c = criar_turma(self.admin, nome='1º C')
        aluno = criar_aluno(self.admin)
        for turma in (self.turma_a, self.turma_b, turma_c, self.turma_a):
            Enturmacao.enturmar(turma, aluno, self.admin)

        self.assertEqual(Enturmacao.objects.filter(aluno=aluno).count(), 4)
        ativa = Enturmacao.objects.get(aluno=aluno, ativo=True)
        self.assertEqual(ativa.turma, self.turma_a)
        motivos = list(Enturmacao.objects.filter(aluno=aluno, ativo=False).values_list('motivo_desenturmacao', flat=True))
        self.assertEqual(len(motivos), 3)
        self.assertTrue(all(m.startswith('Transferido para') for m in motivos))

    def test_turma_com_varios_alunos_e_limite_de_vagas(self):
        self.turma_a.vagas_total = 2
        self.turma_a.save()
        alunos = [criar_aluno(self.admin, nome=f'Aluno {i}') for i in range(3)]
        self.client.force_login(self.admin)
        url = reverse('turma:enturmar_alunos', args=[self.turma_a.pk])
        self.client.post(url, {'alunos': [a.pk for a in alunos]})
        self.assertEqual(self.turma_a.get_total_alunos(), 0, 'Mais alunos que vagas: nada é enturmado')
        self.client.post(url, {'alunos': [a.pk for a in alunos[:2]]})
        self.assertEqual(self.turma_a.get_total_alunos(), 2)

    def test_desenturmar_e_reenturmar_varias_vezes(self):
        aluno = criar_aluno(self.admin)
        self.client.force_login(self.admin)
        for _ in range(3):
            Enturmacao.enturmar(self.turma_a, aluno, self.admin)
            self.client.post(reverse('turma:desenturmar_aluno', args=[self.turma_a.pk, aluno.pk]), {'motivo': 'Teste'})
        self.assertEqual(Enturmacao.objects.filter(aluno=aluno, ativo=False).count(), 3)
        self.assertFalse(Enturmacao.objects.filter(aluno=aluno, ativo=True).exists())


class ProfessoresPorTurmaTest(Base):
    def setUp(self):
        super().setUp()
        self.prof_ana = criar_funcionario(self.admin, nome='Ana', matricula='M-ANA')
        self.prof_joao = criar_funcionario(self.admin, nome='João', matricula='M-JOAO')
        self.login_ana = User.objects.create_user('ana', password='senha-forte-123')
        self.prof_ana.usuario = self.login_ana
        self.prof_ana.save()
        self.associar(self.prof_ana, self.turma_a)
        self.associar(self.prof_joao, self.turma_b)

    def test_cada_turma_de_matematica_tem_seu_professor(self):
        from diario.views import obter_diario
        self.assertEqual(obter_diario(self.turma_a, self.matematica).professor, self.prof_ana)
        self.assertEqual(obter_diario(self.turma_b, self.matematica).professor, self.prof_joao)

    def test_professor_so_acessa_o_proprio_diario(self):
        self.client.force_login(self.login_ana)
        args_a = [self.turma_a.pk, self.matematica.pk, self.divisao.pk]
        args_b = [self.turma_b.pk, self.matematica.pk, self.divisao.pk]
        self.assertEqual(self.client.get(reverse('diario:lancar_notas', args=args_a)).status_code, 200)
        self.assertEqual(self.client.get(reverse('diario:lancar_notas', args=args_b)).status_code, 403)
        self.assertEqual(self.client.get(reverse('diario:turma', args=[self.turma_b.pk])).status_code, 403)
        turmas = list(self.client.get(reverse('diario:home')).context['turmas'])
        self.assertEqual(turmas, [self.turma_a])

        # Coordenação (staff) vê todos os diários
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('diario:lancar_notas', args=args_b)).status_code, 200)

    def test_nao_permite_dois_professores_vigentes_na_mesma_disciplina_e_turma(self):
        dados = {'turma': self.turma_a.pk, 'tipo_associacao': 'DISCIPLINA', 'disciplina': self.matematica.pk,
                 'funcionario': self.prof_joao.pk, 'data_inicio': date(self.ano, 3, 1)}
        self.assertFalse(AssociacaoProfessorForm(dados).is_valid())
        # Mas o mesmo professor pode dar Matemática em outra turma
        dados_c = {**dados, 'turma': criar_turma(self.admin, nome='1º C').pk}
        self.assertTrue(AssociacaoProfessorForm(dados_c).is_valid())

    def test_substituicao_de_professor_fica_no_historico(self):
        atual = AssociacaoProfessor.objects.get(turma=self.turma_a)
        atual.data_termino = date.today() - timedelta(days=1)
        atual.save()
        form = AssociacaoProfessorForm({
            'turma': self.turma_a.pk, 'tipo_associacao': 'DISCIPLINA', 'disciplina': self.matematica.pk,
            'funcionario': self.prof_joao.pk, 'data_inicio': date.today(),
        })
        self.assertTrue(form.is_valid(), form.errors)
        nova = form.save(commit=False)
        nova.usuario_cadastro = self.admin
        nova.save()
        from diario.views import obter_diario
        self.assertEqual(obter_diario(self.turma_a, self.matematica).professor, self.prof_joao)
        self.assertEqual(AssociacaoProfessor.objects.filter(turma=self.turma_a).count(), 2)

    def test_professor_regente_responde_por_todas_as_disciplinas(self):
        portugues = Disciplina.objects.create(nome='Português', codigo='POR')
        self.associar(self.prof_ana, self.turma_b, disciplina=None, tipo='TURMA')
        from diario.views import obter_diario
        self.assertEqual(obter_diario(self.turma_b, portugues).professor, self.prof_ana)
        # A associação específica de disciplina tem prioridade sobre o regente
        self.assertEqual(obter_diario(self.turma_b, self.matematica).professor, self.prof_joao)


class DisciplinaDuplicadaTest(Base):
    def test_nao_cadastra_disciplina_repetida_com_outra_capitalizacao(self):
        for nome in ('MATEMÁTICA', 'matemática', '  Matemática  '):
            self.assertFalse(DisciplinaForm({'nome': nome, 'codigo': 'X1', 'carga_horaria': 40}).is_valid(), nome)
        self.assertTrue(DisciplinaForm({'nome': 'Física', 'codigo': 'FIS', 'carga_horaria': 40}).is_valid())
