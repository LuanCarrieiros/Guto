"""
Teste de navegação ("crawler"): entra como administrador, percorre todas as páginas
alcançáveis a partir do dashboard seguindo os links, e falha se alguma responder com
erro (4xx/5xx). Usa os dados de demonstração para que as telas de detalhe tenham conteúdo.
"""
import re
from collections import Counter
from datetime import date

from django.core.management import call_command
from django.test import TestCase

from guto_system.testing import criar_admin, criar_aluno, criar_funcionario

# Links que alteram dados ou saem do sistema não são seguidos
IGNORAR = re.compile(r'(logout|excluir|delete|remover|fechar|abrir|reativar|encerrar|arquivo|desenturmar|'
                     r'processar|alternar|exportar|/admin/|/static/|/media/)', re.I)
LINK = re.compile(r'href=["\'](/[^"\'#]*)["\']')  # formulários usam POST e não são seguidos
MAX_POR_PADRAO = 3   # quantas URLs do mesmo formato (ex.: /alunos/<id>/) visitar
MAX_PAGINAS = 1500


class NavegacaoCompletaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = criar_admin()
        for i in range(6):
            criar_aluno(cls.admin, nome=f'Aluno Demonstração {i}', nascimento=date(2014, 1, i + 1))
        criar_funcionario(cls.admin)
        call_command('popular_demonstracao', stdout=open('/dev/null', 'w'))

    def test_todas_as_paginas_alcancaveis_respondem(self):
        self.client.force_login(self.admin)
        fila, visitadas, por_padrao, falhas = ['/'], set(), Counter(), []

        while fila and len(visitadas) < MAX_PAGINAS:
            url = fila.pop(0)
            if url in visitadas:
                continue
            padrao = re.sub(r'\d+', '<n>', url.split('?')[0])
            if por_padrao[padrao] >= MAX_POR_PADRAO:
                continue
            por_padrao[padrao] += 1
            visitadas.add(url)

            resposta = self.client.get(url)
            if resposta.status_code >= 400:
                falhas.append(f'{resposta.status_code} {url}')
                continue
            if 'html' not in resposta.get('Content-Type', ''):
                continue
            for link in LINK.findall(resposta.content.decode('utf-8', 'ignore')):
                link = link.replace('&amp;', '&')
                if not IGNORAR.search(link) and link not in visitadas:
                    fila.append(link)

        self.assertGreater(len(visitadas), 100, 'O crawler deveria alcançar a maior parte do sistema')
        self.assertEqual(falhas, [], f'Páginas com erro: {falhas}')
