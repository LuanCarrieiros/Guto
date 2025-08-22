from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date

class Aluno(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]
    
    TIPO_ARQUIVO_CHOICES = [
        ('CORRENTE', 'Arquivo Corrente'),
        ('PERMANENTE', 'Arquivo Permanente'),
    ]
    
    codigo = models.AutoField(primary_key=True, verbose_name="Código")
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    nome_social = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Social")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo")
    
    # Filiação
    nome_mae = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome da Mãe")
    nome_pai = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Pai")
    mae_nao_declarada = models.BooleanField(default=False, verbose_name="Mãe não declarada")
    pai_nao_declarado = models.BooleanField(default=False, verbose_name="Pai não declarado")
    
    # Flags especiais
    aluno_gemeo = models.BooleanField(default=False, verbose_name="Aluno Gêmeo")
    falta_historico_escolar = models.BooleanField(default=False, verbose_name="Falta histórico escolar")
    aluno_exclusivo_aee = models.BooleanField(default=False, verbose_name="Aluno exclusivo de Atividade Complementar/AEE")
    
    # Controle de arquivo
    tipo_arquivo = models.CharField(max_length=20, choices=TIPO_ARQUIVO_CHOICES, default='CORRENTE', verbose_name="Tipo de Arquivo")
    
    # Campos adicionais
    lembrete = models.TextField(blank=True, null=True, verbose_name="Lembrete")
    foto = models.ImageField(upload_to='alunos/fotos/', blank=True, null=True, verbose_name="Foto")
    
    # Dados de auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, related_name='alunos_cadastrados', verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    @property
    def idade(self):
        today = date.today()
        return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))

class DocumentacaoAluno(models.Model):
    aluno = models.OneToOneField(Aluno, on_delete=models.CASCADE, related_name='documentacao')
    
    # Documentos do aluno
    rg = models.CharField(max_length=20, blank=True, null=True, verbose_name="RG")
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name="CPF")
    certidao_nascimento = models.CharField(max_length=50, blank=True, null=True, verbose_name="Certidão de Nascimento")
    titulo_eleitor = models.CharField(max_length=20, blank=True, null=True, verbose_name="Título de Eleitor")
    
    # Flags de controle de documentos
    aluno_nao_possui_documentos = models.BooleanField(default=False, verbose_name="O(a) Aluno(a) não possui os documentos")
    escola_nao_recebeu_documentos = models.BooleanField(default=False, verbose_name="A escola não dispõe ou não recebeu os documentos")
    
    class Meta:
        verbose_name = "Documentação do Aluno"
        verbose_name_plural = "Documentações dos Alunos"

class Responsavel(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='responsaveis')
    nome = models.CharField(max_length=255, verbose_name="Nome do Responsável")
    parentesco = models.CharField(max_length=50, verbose_name="Parentesco")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    
    class Meta:
        verbose_name = "Responsável"
        verbose_name_plural = "Responsáveis"
    
    def __str__(self):
        return f"{self.nome} - {self.parentesco} de {self.aluno.nome}"

class TransporteAluno(models.Model):
    aluno = models.OneToOneField(Aluno, on_delete=models.CASCADE, related_name='transporte')
    utiliza_transporte = models.BooleanField(default=False, verbose_name="Utiliza Transporte Escolar")
    nome_motorista = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Motorista")
    placa_veiculo = models.CharField(max_length=10, blank=True, null=True, verbose_name="Placa do Veículo")
    rota = models.CharField(max_length=100, blank=True, null=True, verbose_name="Rota")
    
    class Meta:
        verbose_name = "Transporte do Aluno"
        verbose_name_plural = "Transportes dos Alunos"

class Matricula(models.Model):
    TIPO_ENSINO_CHOICES = [
        ('INFANTIL', 'Educação Infantil'),
        ('FUNDAMENTAL_I', 'Ensino Fundamental I'),
        ('FUNDAMENTAL_II', 'Ensino Fundamental II'),
        ('MEDIO', 'Ensino Médio'),
        ('EJA', 'Educação de Jovens e Adultos'),
        ('TECNICO', 'Ensino Técnico'),
    ]
    
    TIPO_MATRICULA_CHOICES = [
        ('REGULAR', 'Regular'),
        ('DEPENDENCIA', 'Dependência'),
        ('SUPLENCIA', 'Suplência'),
    ]
    
    TURNO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
        ('NOTURNO', 'Noturno'),
        ('INTEGRAL', 'Integral'),
    ]
    
    CONDICAO_ANTERIOR_CHOICES = [
        ('NOVATO', 'Novato'),
        ('NOVATO_ESCOLA', 'Novato na Escola'),
        ('CONTINUIDADE', 'Continuidade'),
        ('RETORNANDO', 'Retornando'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVA', 'Ativa'),
        ('ENCERRADA', 'Encerrada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='matriculas')
    ano_administrativo = models.IntegerField(verbose_name="Ano Administrativo")
    tipo_ensino = models.CharField(max_length=20, choices=TIPO_ENSINO_CHOICES, verbose_name="Tipo de Ensino")
    serie_ano = models.CharField(max_length=50, verbose_name="Ano/Série/Módulo/Etapa")
    tipo_matricula = models.CharField(max_length=20, choices=TIPO_MATRICULA_CHOICES, default='REGULAR', verbose_name="Tipo de Matrícula")
    turno_preferencial = models.CharField(max_length=20, choices=TURNO_CHOICES, verbose_name="Turno Preferencial")
    data_matricula = models.DateField(verbose_name="Data da Matrícula")
    possui_dependencia = models.BooleanField(default=False, verbose_name="Possui Dependência")
    condicao_anterior = models.CharField(max_length=20, choices=CONDICAO_ANTERIOR_CHOICES, verbose_name="Condição Anterior")
    
    # Dados da escola de origem (para novatos na escola)
    escola_origem = models.CharField(max_length=255, blank=True, null=True, verbose_name="Escola de Origem")
    tipo_rede_origem = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo de Rede")
    pais_origem = models.CharField(max_length=100, blank=True, null=True, verbose_name="País de Origem")
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVA', verbose_name="Status")
    data_encerramento = models.DateField(blank=True, null=True, verbose_name="Data de Encerramento")
    motivo_encerramento = models.TextField(blank=True, null=True, verbose_name="Motivo do Encerramento")
    
    # Condições especiais (LDB Art. 59)
    condicoes_especiais_avaliacao = models.BooleanField(default=False, verbose_name="Condições Especiais de Avaliação")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, related_name='matriculas_cadastradas')
    
    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        unique_together = ['aluno', 'ano_administrativo', 'tipo_matricula']
        ordering = ['-ano_administrativo', '-data_matricula']
    
    def __str__(self):
        return f"Matrícula {self.aluno.codigo} - {self.ano_administrativo} - {self.get_tipo_ensino_display()}"
