import json
from datetime import date

from django.test import TestCase
from django.urls import reverse

from guto_system.testing import criar_admin, criar_aluno, criar_turma
from turma.models import (
    Avaliacao, AvaliacaoDescritiva, Disciplina, DivisaoPeriodoLetivo, Enturmacao, NotaAvaliacao,
    RecuperacaoEspecial, RegistroFrequencia, TipoAvaliacao,
)
from turma.relatorios import calcular_boletim
from .models import DiarioEletronico


class DiarioFluxoTest(TestCase):
    def setUp(self):
        self.user = criar_admin()
        self.client.force_login(self.user)
        ano = date.today().year
        self.turma = criar_turma(self.user)
        self.disciplina = Disciplina.objects.create(nome='Matemática', codigo='MAT')
        self.divisao = DivisaoPeriodoLetivo.objects.create(
            nome='1º Bimestre', tipo_divisao='BIMESTRE', periodo_letivo=str(ano), ordem=1,
            data_inicio=date(ano, 1, 1), data_fim=date(ano, 12, 31),
        )
        self.tipo = TipoAvaliacao.objects.create(nome='Prova')
        self.alunos = [criar_aluno(self.user, nome=f'Aluno {i}') for i in range(2)]
        for aluno in self.alunos:
            Enturmacao.objects.create(turma=self.turma, aluno=aluno, usuario_enturmacao=self.user)
        self.args = [self.turma.pk, self.disciplina.pk, self.divisao.pk]

    def criar_avaliacao(self):
        self.client.post(reverse('diario:gerenciar_avaliacoes', args=self.args), {
            'nome': 'Prova 1', 'tipo_avaliacao': self.tipo.pk, 'peso': '1',
            'data_aplicacao': date.today().isoformat(), 'descricao': '',
        })
        return Avaliacao.objects.get()

    def lancar(self, avaliacao, aluno, nota):
        return self.client.post(
            reverse('diario:lancar_notas', args=self.args),
            data=json.dumps({'aluno_id': aluno.pk, 'avaliacao_id': avaliacao.pk, 'nota': nota}),
            content_type='application/json',
        )

    def test_paginas_do_diario(self):
        self.criar_avaliacao()
        urls = [
            reverse('diario:home'), reverse('diario:turma', args=[self.turma.pk]),
            reverse('diario:disciplina', args=self.args[:2]), reverse('diario:recuperacao', args=self.args[:2]),
        ] + [reverse(f'diario:{n}', args=self.args) for n in (
            'divisao', 'chamada', 'lancar_notas', 'gerenciar_avaliacoes', 'visualizar_avaliacoes', 'pareceres')]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_chamada_registra_presencas(self):
        self.client.post(reverse('diario:chamada', args=self.args), {
            'data_aula': date.today().isoformat(),
            f'toggle_{self.alunos[0].pk}': 'presente',
            f'toggle_{self.alunos[1].pk}': 'ausente',
        })
        situacoes = dict(RegistroFrequencia.objects.values_list('aluno_id', 'situacao'))
        self.assertEqual(situacoes, {self.alunos[0].pk: 'PRESENTE', self.alunos[1].pk: 'AUSENTE'})
        # Refazer a chamada no mesmo dia atualiza em vez de duplicar
        self.client.post(reverse('diario:chamada', args=self.args), {
            'data_aula': date.today().isoformat(), f'toggle_{self.alunos[1].pk}': 'presente',
        })
        self.assertEqual(RegistroFrequencia.objects.filter(situacao='PRESENTE').count(), 2)

    def test_lancamento_de_notas_validado(self):
        avaliacao = self.criar_avaliacao()
        self.assertEqual(self.lancar(avaliacao, self.alunos[0], '8.5').json()['success'], True)
        self.assertEqual(self.lancar(avaliacao, self.alunos[1], '11').status_code, 400)
        externo = criar_aluno(self.user, nome='Fora da turma')
        self.assertEqual(self.lancar(avaliacao, externo, '5').status_code, 400)
        self.lancar(avaliacao, self.alunos[1], '7')
        avaliacao.refresh_from_db()
        self.assertTrue(avaliacao.notas_lancadas)
        self.assertEqual(NotaAvaliacao.objects.count(), 2)

    def test_fechar_diario_bloqueia_alteracoes(self):
        avaliacao = self.criar_avaliacao()
        fechar = reverse('diario:fechar_diario', args=self.args[:2])
        self.assertFalse(self.client.post(fechar).json()['success'], 'Com notas pendentes não fecha')
        for aluno in self.alunos:
            self.lancar(avaliacao, aluno, '9')
        self.assertTrue(self.client.post(fechar).json()['success'])
        self.assertTrue(DiarioEletronico.objects.get(turma=self.turma, disciplina=self.disciplina).diario_fechado)

        self.assertEqual(self.lancar(avaliacao, self.alunos[0], '1').status_code, 403)
        self.client.post(reverse('diario:excluir_avaliacao', args=[avaliacao.pk]))
        self.assertTrue(Avaliacao.objects.filter(pk=avaliacao.pk).exists())

        self.client.post(reverse('diario:abrir_diario', args=self.args[:2]))
        self.assertTrue(self.lancar(avaliacao, self.alunos[0], '1').json()['success'])

    def test_recuperacao_e_parecer_no_boletim(self):
        avaliacao = self.criar_avaliacao()
        self.lancar(avaliacao, self.alunos[0], '3')
        self.lancar(avaliacao, self.alunos[1], '9')

        url = reverse('diario:recuperacao', args=self.args[:2])
        resposta = self.client.get(url)
        self.assertEqual([l['aluno'] for l in resposta.context['linhas']], [self.alunos[0]])
        self.client.post(url, {f'nota_{self.alunos[0].pk}': '7'})
        self.assertEqual(float(RecuperacaoEspecial.objects.get().nota_recuperacao), 7.0)

        self.client.post(reverse('diario:pareceres', args=self.args), {
            f'parecer_{self.alunos[0].pk}': 'Evoluiu bastante no bimestre.',
        })
        self.assertEqual(AvaliacaoDescritiva.objects.count(), 1)

        boletim = calcular_boletim(self.turma, self.alunos[0])
        linha = boletim['linhas'][0]
        self.assertEqual((linha['media'], linha['recuperacao'], linha['situacao']), (7.0, 7.0, 'APROVADO'))
        self.assertEqual(boletim['pareceres'].count(), 1)
        resposta = self.client.get(reverse('turma:boletim_aluno', args=[self.turma.pk, self.alunos[0].pk]))
        self.assertContains(resposta, 'Evoluiu bastante')
