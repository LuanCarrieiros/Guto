from datetime import date

from django.test import TestCase
from django.urls import reverse

from guto_system.testing import criar_admin, criar_aluno
from .models import AulaPrograma, FrequenciaPrograma, ModuloPrograma, ParticipantePrograma, ProgramaPedagogico


class ProgramaFluxoTest(TestCase):
    def setUp(self):
        self.user = criar_admin()
        self.client.force_login(self.user)

    def test_programa_modulo_participante_aula_frequencia(self):
        texto = 'Texto'
        self.client.post(reverse('programa:programa_create'), {
            'nome': 'Reforço de Matemática', 'tipo_programa': 'REFORCO', 'modalidade': 'PRESENCIAL',
            'status': 'ATIVO', 'data_inicio': '2026-02-01', 'data_fim': '2026-06-30', 'carga_horaria_total': 60,
            'vagas_disponiveis': 2, 'descricao': texto, 'objetivos_gerais': texto, 'objetivos_especificos': texto,
            'competencias': texto, 'habilidades': texto, 'publico_alvo': texto,
        })
        programa = ProgramaPedagogico.objects.get()

        resp = self.client.post(reverse('programa:modulo_create') + f'?programa={programa.pk}', {
            'programa': programa.pk, 'ordem': 1, 'nome': 'Frações', 'data_inicio': '2026-03-01',
            'data_fim': '2026-07-30', 'carga_horaria': 20, 'descricao': texto,
            'conteudo_programatico': texto, 'metodologia': texto, 'ativo': 'on',
        })
        self.assertEqual(resp.status_code, 200, 'Módulo fora do período do programa deve ser recusado')
        self.client.post(reverse('programa:modulo_create'), {
            'programa': programa.pk, 'ordem': 1, 'nome': 'Frações', 'data_inicio': '2026-03-01',
            'data_fim': '2026-03-30', 'carga_horaria': 20, 'descricao': texto,
            'conteudo_programatico': texto, 'metodologia': texto, 'ativo': 'on',
        })
        modulo = ModuloPrograma.objects.get()

        alunos = [criar_aluno(self.user, nome=f'Aluno {i}') for i in range(2)]
        for aluno in alunos:
            self.client.post(reverse('programa:participante_create', args=[programa.pk]), {
                'aluno': aluno.pk, 'data_inscricao': '2026-02-01', 'situacao': 'ATIVO',
            })
        self.assertEqual(ParticipantePrograma.objects.count(), 2)

        self.client.post(reverse('programa:aula_create'), {
            'modulo': modulo.pk, 'numero_aula': 1, 'titulo': 'Introdução', 'tipo_aula': 'TEORICA',
            'data_planejada': '2026-03-02', 'horario_inicio': '14:00', 'horario_fim': '15:00',
            'carga_horaria': '1.00', 'objetivos': texto, 'conteudo': texto, 'metodologia': texto,
            'status': 'PLANEJADA',
        })
        aula = AulaPrograma.objects.get()

        presente = ParticipantePrograma.objects.get(aluno=alunos[0])
        self.client.post(reverse('programa:frequencia_aula', args=[aula.pk]), {
            'presentes': [presente.pk], f'justificativa_{alunos[1].pk}': '',
        })
        aula.refresh_from_db()
        self.assertEqual((aula.presentes, aula.ausentes, aula.status), (1, 1, 'REALIZADA'))
        self.assertEqual(FrequenciaPrograma.objects.count(), 2)
        presente.refresh_from_db()
        self.assertEqual(float(presente.frequencia_total), 100.0)

        for url in (reverse('programa:programa_home'), reverse('programa:programa_list'),
                    reverse('programa:modulo_list'), reverse('programa:aula_list'),
                    reverse('programa:programa_detail', args=[programa.pk]),
                    reverse('programa:programa_edit', args=[programa.pk]),
                    reverse('programa:modulo_detail', args=[modulo.pk]),
                    reverse('programa:modulo_edit', args=[modulo.pk]),
                    reverse('programa:participante_list', args=[programa.pk]),
                    reverse('programa:frequencia_aula', args=[aula.pk])):
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_inscricao_respeita_vagas(self):
        programa = ProgramaPedagogico.objects.create(
            nome='P', descricao='d', tipo_programa='REGULAR', data_inicio=date(2026, 1, 1),
            data_fim=date(2026, 12, 31), carga_horaria_total=10, objetivos_gerais='o', objetivos_especificos='o',
            competencias='c', habilidades='h', publico_alvo='p', vagas_disponiveis=0, usuario_cadastro=self.user,
        )
        resp = self.client.get(reverse('programa:participante_create', args=[programa.pk]))
        self.assertRedirects(resp, reverse('programa:participante_list', args=[programa.pk]))
