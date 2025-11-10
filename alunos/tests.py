from django.test import TestCase, Client
from django.contrib.auth.models import User
from datetime import date, timedelta
from alunos.models import Aluno, Matricula, DocumentacaoAluno, Responsavel, TransporteAluno


class AlunoModelTest(TestCase):
    """Testes para o Model Aluno (Camada de Domínio)"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.aluno = Aluno.objects.create(
            nome='João da Silva',
            data_nascimento=date(2010, 5, 15),
            sexo='M',
            nome_mae='Maria da Silva',
            nome_pai='José da Silva',
            usuario_cadastro=self.user
        )

    def test_criacao_aluno(self):
        """Teste 1: Verifica se o aluno foi criado corretamente"""
        self.assertEqual(self.aluno.nome, 'João da Silva')
        self.assertEqual(self.aluno.sexo, 'M')
        self.assertIsNotNone(self.aluno.codigo)
        self.assertEqual(self.aluno.tipo_arquivo, 'CORRENTE')

    def test_calculo_idade(self):
        """Teste 2: Verifica o cálculo correto da idade do aluno"""
        # Aluno nascido em 2010, idade deve ser aproximadamente 14-15 anos
        idade_esperada = date.today().year - 2010
        idade_calculada = self.aluno.idade

        # A idade pode variar por 1 ano dependendo do mês/dia atual
        self.assertIn(idade_calculada, [idade_esperada - 1, idade_esperada])

    def test_str_representation(self):
        """Teste 3: Verifica a representação em string do aluno"""
        expected_str = f"{self.aluno.codigo} - João da Silva"
        self.assertEqual(str(self.aluno), expected_str)

    def test_aluno_gemeo_flag(self):
        """Teste 4: Verifica a flag de aluno gêmeo"""
        self.assertFalse(self.aluno.aluno_gemeo)

        aluno_gemeo = Aluno.objects.create(
            nome='Pedro da Silva',
            data_nascimento=date(2010, 5, 15),
            sexo='M',
            nome_mae='Maria da Silva',
            aluno_gemeo=True,
            usuario_cadastro=self.user
        )
        self.assertTrue(aluno_gemeo.aluno_gemeo)

    def test_arquivo_permanente(self):
        """Teste 5: Verifica movimentação para arquivo permanente"""
        self.assertEqual(self.aluno.tipo_arquivo, 'CORRENTE')

        # Mover para arquivo permanente
        self.aluno.tipo_arquivo = 'PERMANENTE'
        self.aluno.save()

        aluno_atualizado = Aluno.objects.get(codigo=self.aluno.codigo)
        self.assertEqual(aluno_atualizado.tipo_arquivo, 'PERMANENTE')


class MatriculaModelTest(TestCase):
    """Testes para o Model Matrícula (Camada de Domínio)"""

    def setUp(self):
        """Configuração inicial para os testes de matrícula"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.aluno = Aluno.objects.create(
            nome='Ana Paula',
            data_nascimento=date(2012, 8, 20),
            sexo='F',
            usuario_cadastro=self.user
        )

    def test_criacao_matricula(self):
        """Teste 6: Verifica criação de matrícula"""
        matricula = Matricula.objects.create(
            aluno=self.aluno,
            ano_administrativo=2025,
            tipo_ensino='FUNDAMENTAL_I',
            serie_ano='3º Ano',
            turno_preferencial='MATUTINO',
            data_matricula=date.today(),
            condicao_anterior='NOVATO',
            usuario_cadastro=self.user
        )

        self.assertEqual(matricula.aluno, self.aluno)
        self.assertEqual(matricula.status, 'ATIVA')
        self.assertEqual(matricula.tipo_ensino, 'FUNDAMENTAL_I')

    def test_unique_together_matricula(self):
        """Teste 7: Verifica constraint de unicidade de matrícula"""
        # Criar primeira matrícula
        Matricula.objects.create(
            aluno=self.aluno,
            ano_administrativo=2025,
            tipo_ensino='FUNDAMENTAL_I',
            serie_ano='3º Ano',
            turno_preferencial='MATUTINO',
            data_matricula=date.today(),
            condicao_anterior='NOVATO',
            tipo_matricula='REGULAR',
            usuario_cadastro=self.user
        )

        # Tentar criar matrícula duplicada deve falhar
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Matricula.objects.create(
                aluno=self.aluno,
                ano_administrativo=2025,
                tipo_ensino='FUNDAMENTAL_I',
                serie_ano='3º Ano',
                turno_preferencial='MATUTINO',
                data_matricula=date.today(),
                condicao_anterior='NOVATO',
                tipo_matricula='REGULAR',
                usuario_cadastro=self.user
            )

    def test_encerramento_matricula(self):
        """Teste 8: Verifica encerramento de matrícula"""
        matricula = Matricula.objects.create(
            aluno=self.aluno,
            ano_administrativo=2025,
            tipo_ensino='FUNDAMENTAL_I',
            serie_ano='3º Ano',
            turno_preferencial='MATUTINO',
            data_matricula=date.today(),
            condicao_anterior='NOVATO',
            usuario_cadastro=self.user
        )

        # Encerrar matrícula
        matricula.status = 'ENCERRADA'
        matricula.data_encerramento = date.today()
        matricula.motivo_encerramento = 'Transferência'
        matricula.save()

        matricula_atualizada = Matricula.objects.get(id=matricula.id)
        self.assertEqual(matricula_atualizada.status, 'ENCERRADA')
        self.assertIsNotNone(matricula_atualizada.data_encerramento)


class DocumentacaoAlunoModelTest(TestCase):
    """Testes para o Model DocumentacaoAluno (Camada de Domínio)"""

    def setUp(self):
        """Configuração inicial para testes de documentação"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.aluno = Aluno.objects.create(
            nome='Carlos Eduardo',
            data_nascimento=date(2011, 3, 10),
            sexo='M',
            usuario_cadastro=self.user
        )

    def test_criacao_documentacao(self):
        """Teste 9: Verifica criação de documentação do aluno"""
        doc = DocumentacaoAluno.objects.create(
            aluno=self.aluno,
            cpf='123.456.789-00',
            rg='MG-12.345.678'
        )

        self.assertEqual(doc.aluno, self.aluno)
        self.assertEqual(doc.cpf, '123.456.789-00')
        self.assertFalse(doc.aluno_nao_possui_documentos)

    def test_one_to_one_relationship(self):
        """Teste 10: Verifica relacionamento OneToOne com Aluno"""
        doc = DocumentacaoAluno.objects.create(
            aluno=self.aluno,
            cpf='987.654.321-00'
        )

        # Acessar documentação através do aluno
        self.assertEqual(self.aluno.documentacao, doc)
        self.assertEqual(self.aluno.documentacao.cpf, '987.654.321-00')


class AlunoViewsTest(TestCase):
    """Testes para Views de Aluno (Camada de Persistência/API)"""

    def setUp(self):
        """Configuração inicial para testes de views"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        self.aluno = Aluno.objects.create(
            nome='Maria Fernanda',
            data_nascimento=date(2013, 7, 25),
            sexo='F',
            usuario_cadastro=self.user
        )

    def test_aluno_list_view(self):
        """Teste 11: Verifica listagem de alunos (GET)"""
        response = self.client.get('/alunos/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maria Fernanda')

    def test_aluno_detail_view(self):
        """Teste 12: Verifica detalhes de um aluno (GET)"""
        response = self.client.get(f'/alunos/{self.aluno.codigo}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maria Fernanda')

    def test_aluno_create_view(self):
        """Teste 13: Verifica criação de aluno via POST"""
        data = {
            'nome': 'Roberto Alves',
            'data_nascimento': '2014-09-12',
            'sexo': 'M',
            'nome_mae': 'Sandra Alves',
        }

        response = self.client.post('/alunos/cadastrar/', data)

        # Verifica se foi criado (redirect ou success)
        self.assertIn(response.status_code, [200, 201, 302])

        # Verifica se o aluno foi criado no banco
        self.assertTrue(
            Aluno.objects.filter(nome='Roberto Alves').exists()
        )

    def test_aluno_edit_view(self):
        """Teste 14: Verifica edição de aluno via POST"""
        data = {
            'nome': 'Maria Fernanda Silva',  # Nome alterado
            'data_nascimento': '2013-07-25',
            'sexo': 'F',
        }

        response = self.client.post(
            f'/alunos/{self.aluno.codigo}/editar/',
            data
        )

        # Recarregar aluno do banco
        self.aluno.refresh_from_db()

        # Verifica se o nome foi atualizado
        self.assertIn('Silva', self.aluno.nome)

    def test_aluno_search(self):
        """Teste 15: Verifica busca de alunos"""
        response = self.client.get('/alunos/', {'q': 'Maria'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maria Fernanda')
