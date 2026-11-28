from django.test import TestCase
from django.urls import reverse

from guto_system.testing import criar_admin, criar_aluno, criar_rota_completa
from .models import AlunoTransporte, ManutencaoVeiculo, PontoParada, RegistroViagem


class TransporteFluxoTest(TestCase):
    def setUp(self):
        self.user = criar_admin()
        self.client.force_login(self.user)
        self.motorista, self.veiculo, self.rota, self.ponto = criar_rota_completa(self.user)

    def test_paginas_do_modulo(self):
        urls = [
            reverse('transporte:transporte_home'), reverse('transporte:relatorio_transporte'),
            reverse('transporte:motorista_list'), reverse('transporte:veiculo_list'), reverse('transporte:rota_list'),
            reverse('transporte:aluno_transporte_list'), reverse('transporte:viagem_create'),
            reverse('transporte:motorista_detail', args=[self.motorista.pk]),
            reverse('transporte:motorista_edit', args=[self.motorista.pk]),
            reverse('transporte:veiculo_detail', args=[self.veiculo.pk]),
            reverse('transporte:veiculo_edit', args=[self.veiculo.pk]),
            reverse('transporte:rota_detail', args=[self.rota.pk]),
            reverse('transporte:rota_edit', args=[self.rota.pk]),
            reverse('transporte:ponto_create', args=[self.rota.pk]),
            reverse('transporte:manutencao_create', args=[self.veiculo.pk]),
            reverse('transporte:aluno_transporte_create', args=[self.rota.pk]),
            reverse('transporte:ajax_pontos_rota', args=[self.rota.pk]),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_vincular_aluno_registrar_viagem_e_manutencao(self):
        aluno = criar_aluno(self.user)
        self.client.post(reverse('transporte:aluno_transporte_create', args=[self.rota.pk]), {
            'aluno': aluno.pk, 'ponto_embarque': self.ponto.pk, 'ponto_desembarque': self.ponto.pk,
            'responsavel_nome': 'Mãe', 'responsavel_telefone': '9999', 'responsavel_endereco': 'Rua',
            'data_inicio': '2026-02-01', 'situacao': 'ATIVO', 'ativo': 'on',
        })
        self.assertEqual(AlunoTransporte.objects.filter(rota=self.rota).count(), 1)

        self.client.post(reverse('transporte:viagem_create') + f'?rota={self.rota.pk}', {
            'rota': self.rota.pk, 'motorista': self.motorista.pk, 'veiculo': self.veiculo.pk,
            'data_viagem': '2026-03-02', 'tipo_viagem': 'IDA', 'km_inicial': 1000, 'km_final': 1030,
            'alunos_transportados': 1, 'concluida': 'on',
        })
        self.assertEqual(RegistroViagem.objects.count(), 1)
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.km_atual, 1030)
        resp = self.client.get(reverse('transporte:veiculo_detail', args=[self.veiculo.pk]))
        self.assertEqual(resp.context['total_km'], 30)

        self.client.post(reverse('transporte:manutencao_create', args=[self.veiculo.pk]), {
            'tipo_manutencao': 'PREVENTIVA', 'descricao': 'Troca de óleo', 'data_agendamento': '2026-03-10',
            'status': 'AGENDADA', 'km_veiculo': 1030, 'oficina_prestador': 'Oficina X',
        })
        self.assertEqual(ManutencaoVeiculo.objects.filter(veiculo=self.veiculo).count(), 1)

    def test_ponto_de_parada_e_exclusao_de_motorista_com_rota(self):
        self.client.post(reverse('transporte:ponto_create', args=[self.rota.pk]), {
            'nome': 'Escola', 'endereco': 'Rua da Escola', 'horario_ida': '07:00', 'horario_volta': '12:10',
            'ordem': 2, 'ativo': 'on',
        })
        self.assertEqual(PontoParada.objects.filter(rota=self.rota).count(), 2)
        # Motorista com rota ativa não pode ser excluído
        resp = self.client.get(reverse('transporte:motorista_delete', args=[self.motorista.pk]))
        self.assertRedirects(resp, reverse('transporte:motorista_detail', args=[self.motorista.pk]))
