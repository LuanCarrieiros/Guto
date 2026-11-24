from django.test import TestCase
from django.urls import reverse

from guto_system.testing import criar_admin, criar_aluno
from .models import AssociacaoItinerarioUnidade, EnturmacaoItinerario, ItinerarioFormativo, UnidadeCurricular


class EscolaFluxoTest(TestCase):
    def setUp(self):
        self.user = criar_admin()
        self.client.force_login(self.user)

    def test_itinerario_unidade_e_enturmacao(self):
        self.client.post(reverse('escola:itinerario_create'), {
            'nome': 'Ciência de Dados', 'carga_horaria_total': 120, 'areas_conhecimento': 'MATEMATICA',
            'habilidades': 'Estatística', 'vagas_disponiveis': 1,
        })
        itinerario = ItinerarioFormativo.objects.get()
        self.client.post(reverse('escola:unidade_create'), {
            'nome': 'Estatística I', 'carga_horaria': 40, 'ementa': 'Introdução', 'habilidades_especificas': 'Médias',
        })
        unidade = UnidadeCurricular.objects.get()

        self.client.post(reverse('escola:associar_unidade', args=[itinerario.pk]), {'unidade': unidade.pk, 'ordem': 1})
        self.assertTrue(AssociacaoItinerarioUnidade.objects.filter(itinerario=itinerario, unidade=unidade).exists())

        aluno = criar_aluno(self.user)
        self.client.post(reverse('escola:enturmacao_create', args=[itinerario.pk]), {'aluno': aluno.pk})
        self.assertEqual(EnturmacaoItinerario.objects.count(), 1)

        # Sem vagas: a tela de enturmação redireciona com erro
        resp = self.client.get(reverse('escola:enturmacao_create', args=[itinerario.pk]))
        self.assertRedirects(resp, reverse('escola:itinerario_detail', args=[itinerario.pk]))

        for url in (reverse('escola:escola_home'), reverse('escola:itinerario_list'), reverse('escola:unidade_list'),
                    reverse('escola:itinerario_detail', args=[itinerario.pk]),
                    reverse('escola:unidade_detail', args=[unidade.pk]),
                    reverse('escola:unidade_edit', args=[unidade.pk])):
            self.assertEqual(self.client.get(url).status_code, 200, url)

        enturmacao = EnturmacaoItinerario.objects.get()
        self.client.post(reverse('escola:enturmacao_delete', args=[enturmacao.pk]), {'confirmar': 'sim'})
        self.assertFalse(EnturmacaoItinerario.objects.exists())
