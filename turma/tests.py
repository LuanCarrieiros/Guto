from django.test import TestCase, Client
from django.contrib.auth.models import User
from datetime import date
from turma.models import Turma, Disciplina, Enturmacao, Conceito, TipoAvaliacao, Avaliacao, NotaAvaliacao
from alunos.models import Aluno


class TurmaModelTest(TestCase):
    """Testes para o Model Turma (Camada de Domínio)"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.turma = Turma.objects.create(
            nome='3º Ano A',
            periodo_letivo='2025',
            tipo_ensino='ENSINO_FUNDAMENTAL_I',
            ano_serie='3_ANO',
            turno='MATUTINO',
            vagas_total=30,
            usuario_criacao=self.user
        )

    def test_criacao_turma(self):
        """Teste 1: Verifica se a turma foi criada corretamente"""
        self.assertEqual(self.turma.nome, '3º Ano A')
        self.assertEqual(self.turma.periodo_letivo, '2025')
        self.assertEqual(self.turma.vagas_total, 30)
        self.assertFalse(self.turma.diario_fechado)

    def test_str_representation(self):
        """Teste 2: Verifica a representação em string da turma"""
        expected_str = "3º Ano A - 2025"
        self.assertEqual(str(self.turma), expected_str)

    def test_get_total_alunos_vazia(self):
        """Teste 3: Verifica total de alunos em turma vazia"""
        total = self.turma.get_total_alunos()
        self.assertEqual(total, 0)

    def test_get_vagas_disponiveis(self):
        """Teste 4: Verifica cálculo de vagas disponíveis"""
        # Turma vazia deve ter todas as vagas disponíveis
        vagas = self.turma.get_vagas_disponiveis()
        self.assertEqual(vagas, 30)

        # Criar aluno e enturmar
        aluno = Aluno.objects.create(
            nome='João',
            data_nascimento=date(2015, 1, 1),
            sexo='M',
            usuario_cadastro=self.user
        )
        Enturmacao.objects.create(
            turma=self.turma,
            aluno=aluno,
            ativo=True,
            usuario_enturmacao=self.user
        )

        # Agora deve ter 29 vagas disponíveis
        vagas = self.turma.get_vagas_disponiveis()
        self.assertEqual(vagas, 29)

    def test_get_percentual_ocupacao(self):
        """Teste 5: Verifica cálculo do percentual de ocupação"""
        # Turma vazia = 0% de ocupação
        percentual = self.turma.get_percentual_ocupacao()
        self.assertEqual(percentual, 0)

        # Criar 10 alunos e enturmar
        for i in range(10):
            aluno = Aluno.objects.create(
                nome=f'Aluno {i}',
                data_nascimento=date(2015, 1, 1),
                sexo='M',
                usuario_cadastro=self.user
            )
            Enturmacao.objects.create(
                turma=self.turma,
                aluno=aluno,
                ativo=True,
                usuario_enturmacao=self.user
            )

        # 10 de 30 = 33%
        percentual = self.turma.get_percentual_ocupacao()
        self.assertEqual(percentual, 33)

    def test_unique_together_turma(self):
        """Teste 6: Verifica constraint de nome único por período letivo"""
        from django.db import IntegrityError

        # Tentar criar turma com mesmo nome e período deve falhar
        with self.assertRaises(IntegrityError):
            Turma.objects.create(
                nome='3º Ano A',
                periodo_letivo='2025',
                tipo_ensino='ENSINO_FUNDAMENTAL_I',
                ano_serie='3_ANO',
                turno='VESPERTINO',
                usuario_criacao=self.user
            )


class DisciplinaModelTest(TestCase):
    """Testes para o Model Disciplina (Camada de Domínio)"""

    def setUp(self):
        """Configuração inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_criacao_disciplina(self):
        """Teste 7: Verifica criação de disciplina"""
        disciplina = Disciplina.objects.create(
            nome='Matemática',
            carga_horaria=80,
            ativo=True
        )

        self.assertEqual(disciplina.nome, 'Matemática')
        self.assertEqual(disciplina.carga_horaria, 80)
        self.assertTrue(disciplina.ativo)
        # Código deve ser gerado automaticamente
        self.assertIsNotNone(disciplina.codigo)

    def test_codigo_automatico(self):
        """Teste 8: Verifica geração automática de código"""
        disciplina = Disciplina.objects.create(
            nome='Matemática',
            carga_horaria=80
        )

        # Código deve começar com MAT (mapeamento especial)
        self.assertTrue(disciplina.codigo.startswith('MAT'))

    def test_str_representation(self):
        """Teste 9: Verifica representação em string da disciplina"""
        disciplina = Disciplina.objects.create(
            nome='Português',
            carga_horaria=80
        )

        self.assertEqual(str(disciplina), 'Português')


class EnturmacaoModelTest(TestCase):
    """Testes para o Model Enturmação (Camada de Domínio)"""

    def setUp(self):
        """Configuração inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.turma = Turma.objects.create(
            nome='4º Ano B',
            periodo_letivo='2025',
            tipo_ensino='ENSINO_FUNDAMENTAL_I',
            ano_serie='4_ANO',
            turno='VESPERTINO',
            usuario_criacao=self.user
        )

        self.aluno = Aluno.objects.create(
            nome='Ana Silva',
            data_nascimento=date(2014, 6, 15),
            sexo='F',
            usuario_cadastro=self.user
        )

    def test_criacao_enturmacao(self):
        """Teste 10: Verifica criação de enturmação"""
        enturmacao = Enturmacao.objects.create(
            turma=self.turma,
            aluno=self.aluno,
            ativo=True,
            usuario_enturmacao=self.user
        )

        self.assertEqual(enturmacao.turma, self.turma)
        self.assertEqual(enturmacao.aluno, self.aluno)
        self.assertTrue(enturmacao.ativo)

    def test_unica_enturmacao_ativa(self):
        """Teste 11: Verifica constraint de enturmação única ativa"""
        # Criar primeira enturmação ativa
        Enturmacao.objects.create(
            turma=self.turma,
            aluno=self.aluno,
            ativo=True,
            usuario_enturmacao=self.user
        )

        # Criar segunda turma
        turma2 = Turma.objects.create(
            nome='5º Ano A',
            periodo_letivo='2025',
            tipo_ensino='ENSINO_FUNDAMENTAL_I',
            ano_serie='5_ANO',
            turno='MATUTINO',
            usuario_criacao=self.user
        )

        # Tentar criar segunda enturmação ativa para o mesmo aluno deve falhar
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Enturmacao.objects.create(
                turma=turma2,
                aluno=self.aluno,
                ativo=True,
                usuario_enturmacao=self.user
            )

    def test_desenturmacao(self):
        """Teste 12: Verifica desenturmação de aluno"""
        enturmacao = Enturmacao.objects.create(
            turma=self.turma,
            aluno=self.aluno,
            ativo=True,
            usuario_enturmacao=self.user
        )

        # Desenturmar
        enturmacao.ativo = False
        enturmacao.data_desenturmacao = date.today()
        enturmacao.motivo_desenturmacao = 'Transferência'
        enturmacao.save()

        enturmacao_atualizada = Enturmacao.objects.get(id=enturmacao.id)
        self.assertFalse(enturmacao_atualizada.ativo)
        self.assertIsNotNone(enturmacao_atualizada.data_desenturmacao)


class AvaliacaoModelTest(TestCase):
    """Testes para o Model Avaliação (Camada de Domínio)"""

    def setUp(self):
        """Configuração inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.turma = Turma.objects.create(
            nome='2º Ano C',
            periodo_letivo='2025',
            tipo_ensino='ENSINO_FUNDAMENTAL_I',
            ano_serie='2_ANO',
            turno='MATUTINO',
            usuario_criacao=self.user
        )

        self.disciplina = Disciplina.objects.create(
            nome='História',
            carga_horaria=60
        )

        self.tipo_avaliacao = TipoAvaliacao.objects.create(
            nome='Prova',
            descricao='Avaliação escrita',
            peso_default=2.0
        )

    def test_criacao_tipo_avaliacao(self):
        """Teste 13: Verifica criação de tipo de avaliação"""
        self.assertEqual(self.tipo_avaliacao.nome, 'Prova')
        self.assertEqual(self.tipo_avaliacao.peso_default, 2.0)
        self.assertTrue(self.tipo_avaliacao.ativo)

    def test_str_representation_tipo_avaliacao(self):
        """Teste 14: Verifica representação em string do tipo"""
        self.assertEqual(str(self.tipo_avaliacao), 'Prova')


class ConceitoModelTest(TestCase):
    """Testes para o Model Conceito (Camada de Domínio)"""

    def setUp(self):
        """Configuração inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_criacao_conceito(self):
        """Teste 15: Verifica criação de conceito"""
        conceito = Conceito.objects.create(
            nome='A',
            descricao='Excelente',
            valor_numerico=9.0,
            usuario_criacao=self.user
        )

        self.assertEqual(conceito.nome, 'A')
        self.assertEqual(conceito.descricao, 'Excelente')
        self.assertEqual(float(conceito.valor_numerico), 9.0)
        self.assertTrue(conceito.ativo)

    def test_str_representation_conceito(self):
        """Teste 16: Verifica representação em string do conceito"""
        conceito = Conceito.objects.create(
            nome='B',
            descricao='Bom',
            valor_numerico=7.5,
            usuario_criacao=self.user
        )

        expected_str = "B - Bom"
        self.assertEqual(str(conceito), expected_str)


class TurmaViewsTest(TestCase):
    """Testes para Views de Turma (Camada de Persistência/API)"""

    def setUp(self):
        """Configuração inicial para testes de views"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        self.turma = Turma.objects.create(
            nome='1º Ano D',
            periodo_letivo='2025',
            tipo_ensino='ENSINO_FUNDAMENTAL_I',
            ano_serie='1_ANO',
            turno='INTEGRAL',
            usuario_criacao=self.user
        )

    def test_turma_list_view(self):
        """Teste 17: Verifica listagem de turmas (GET)"""
        response = self.client.get('/turmas/turmas/')  # URL COMPLETA: /turmas/turmas/

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1º Ano D')

    def test_turma_detail_view(self):
        """Teste 18: Verifica detalhes de uma turma (GET)"""
        response = self.client.get(f'/turmas/turmas/{self.turma.id}/')  # URL COMPLETA

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1º Ano D')
