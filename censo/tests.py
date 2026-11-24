from datetime import date

from django.test import TestCase
from django.urls import reverse

from alunos.models import Matricula
from guto_system.testing import criar_admin, criar_aluno


class CensoTest(TestCase):
    def setUp(self):
        self.user = criar_admin()
        self.client.force_login(self.user)
        aluno = criar_aluno(self.user)
        Matricula.objects.create(
            aluno=aluno, ano_administrativo=date.today().year, tipo_ensino='FUNDAMENTAL_I', serie_ano='5º ano',
            turno_preferencial='MATUTINO', data_matricula=date.today(), condicao_anterior='NOVATO',
            usuario_cadastro=self.user,
        )

    def test_paginas(self):
        for nome in ('censo_home', 'censo_escolar', 'relatorios', 'relatorio_matriculas',
                     'relatorio_funcionarios', 'relatorio_estatisticas'):
            self.assertEqual(self.client.get(reverse(f'censo:{nome}')).status_code, 200, nome)

    def test_exportacao_csv_e_json(self):
        resp = self.client.get(reverse('censo:exportar_dados', args=['matriculas']) + '?formato=csv')
        self.assertEqual(resp['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('5º ano', resp.content.decode('utf-8-sig'))
        resp = self.client.get(reverse('censo:exportar_dados', args=['matriculas']))
        self.assertEqual(resp.json()['total'], 1)
        self.assertEqual(self.client.get(reverse('censo:exportar_dados', args=['xyz'])).status_code, 400)
