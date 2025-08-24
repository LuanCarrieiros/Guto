from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator
from datetime import date, datetime
from decimal import Decimal
from alunos.models import Aluno

class Conceito(models.Model):
    """Model para Conceitos utilizados na avaliação (RNF1102, RNF1203, RNF1401)"""
    nome = models.CharField(max_length=10, unique=True, verbose_name="Nome do Conceito")
    descricao = models.CharField(max_length=100, verbose_name="Descrição")
    valor_numerico = models.DecimalField(
        max_digits=4, decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Valor Numérico Equivalente"
    )
    ativo = models.BooleanField(default=True, verbose_name="Conceito Ativo")
    cor_display = models.CharField(max_length=7, default='#3B82F6', verbose_name="Cor para Exibição")
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Criado por")
    
    class Meta:
        verbose_name = "Conceito"
        verbose_name_plural = "Conceitos"
        ordering = ['valor_numerico']
    
    def __str__(self):
        return f"{self.nome} - {self.descricao}"

class GrupoConceito(models.Model):
    """Model para Grupos de Conceitos"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Grupo")
    conceitos = models.ManyToManyField(Conceito, verbose_name="Conceitos do Grupo")
    ativo = models.BooleanField(default=True, verbose_name="Grupo Ativo")
    
    class Meta:
        verbose_name = "Grupo de Conceito"
        verbose_name_plural = "Grupos de Conceitos"
    
    def __str__(self):
        return self.nome

class Turma(models.Model):
    """Model para Turmas"""
    TIPO_ENSINO_CHOICES = [
        ('EDUCACAO_INFANTIL', 'Educação Infantil'),
        ('ENSINO_FUNDAMENTAL_I', 'Ensino Fundamental I'),
        ('ENSINO_FUNDAMENTAL_II', 'Ensino Fundamental II'),
        ('ENSINO_MEDIO', 'Ensino Médio'),
        ('EJA', 'Educação de Jovens e Adultos'),
        ('TECNICO', 'Técnico'),
    ]
    
    ANO_SERIE_CHOICES = [
        ('BERÇARIO', 'Berçário'),
        ('MATERNAL_I', 'Maternal I'),
        ('MATERNAL_II', 'Maternal II'),
        ('PRE_I', 'Pré I'),
        ('PRE_II', 'Pré II'),
        ('1_ANO', '1º Ano'),
        ('2_ANO', '2º Ano'),
        ('3_ANO', '3º Ano'),
        ('4_ANO', '4º Ano'),
        ('5_ANO', '5º Ano'),
        ('6_ANO', '6º Ano'),
        ('7_ANO', '7º Ano'),
        ('8_ANO', '8º Ano'),
        ('9_ANO', '9º Ano'),
        ('1_SERIE', '1ª Série'),
        ('2_SERIE', '2ª Série'),
        ('3_SERIE', '3ª Série'),
    ]
    
    TURNO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
        ('NOTURNO', 'Noturno'),
        ('INTEGRAL', 'Integral'),
    ]
    
    nome = models.CharField(max_length=255, verbose_name="Nome da Turma")
    periodo_letivo = models.CharField(max_length=4, default=str(date.today().year), verbose_name="Período Letivo")
    tipo_ensino = models.CharField(max_length=50, choices=TIPO_ENSINO_CHOICES, verbose_name="Tipo de Ensino")
    ano_serie = models.CharField(max_length=50, choices=ANO_SERIE_CHOICES, verbose_name="Ano/Série")
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, verbose_name="Turno")
    diario_fechado = models.BooleanField(default=False, verbose_name="Diário Fechado")
    vagas_total = models.IntegerField(default=30, verbose_name="Total de Vagas")
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação", null=True, blank=True)
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Criado por", null=True, blank=True)
    
    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        unique_together = ['nome', 'periodo_letivo']
        ordering = ['periodo_letivo', 'ano_serie', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.periodo_letivo}"
    
    def get_total_alunos(self):
        """Retorna total de alunos enturmados"""
        return self.enturmacoes.filter(ativo=True).count()
    
    def get_vagas_disponiveis(self):
        """Retorna número de vagas disponíveis"""
        return self.vagas_total - self.get_total_alunos()
    
    def get_alunos_enturmados(self):
        """Retorna queryset dos alunos enturmados na turma"""
        return Aluno.objects.filter(
            enturmacoes__turma=self,
            enturmacoes__ativo=True
        )

class Disciplina(models.Model):
    """Model para Disciplinas"""
    nome = models.CharField(max_length=255, verbose_name="Nome da Disciplina")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código da Disciplina")
    avalia_por_conceito = models.BooleanField(default=False, verbose_name="Avalia por Conceito")
    carga_horaria = models.IntegerField(default=40, verbose_name="Carga Horária")
    ativo = models.BooleanField(default=True, verbose_name="Disciplina Ativa")
    
    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class DivisaoPeriodoLetivo(models.Model):
    """Model para Divisões do Período Letivo (Bimestres, Trimestres, etc.)"""
    TIPO_DIVISAO_CHOICES = [
        ('BIMESTRE', 'Bimestre'),
        ('TRIMESTRE', 'Trimestre'),
        ('SEMESTRE', 'Semestre'),
        ('ANUAL', 'Anual'),
    ]
    
    nome = models.CharField(max_length=50, verbose_name="Nome da Divisão")
    tipo_divisao = models.CharField(max_length=15, choices=TIPO_DIVISAO_CHOICES, verbose_name="Tipo de Divisão")
    periodo_letivo = models.CharField(max_length=4, verbose_name="Período Letivo")
    ordem = models.IntegerField(verbose_name="Ordem")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Fim")
    ativo = models.BooleanField(default=True, verbose_name="Divisão Ativa")
    
    class Meta:
        verbose_name = "Divisão do Período Letivo"
        verbose_name_plural = "Divisões do Período Letivo"
        ordering = ['periodo_letivo', 'ordem']
        unique_together = ['periodo_letivo', 'ordem']
    
    def __str__(self):
        return f"{self.nome} - {self.periodo_letivo}"

class LancamentoNota(models.Model):
    """Model para Lançamento de Notas e Conceitos (RF1103-RF1108)"""
    TIPO_LANCAMENTO_CHOICES = [
        ('AVALIACAO_FREQUENCIA', 'Avaliação/Frequência'),
        ('AVALIACAO', 'Avaliação'),
        ('FREQUENCIA', 'Frequência'),
    ]
    
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, verbose_name="Disciplina")
    divisao_periodo = models.ForeignKey(DivisaoPeriodoLetivo, on_delete=models.CASCADE, verbose_name="Divisão do Período")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    
    # Campos de avaliação
    nota = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Nota"
    )
    conceito = models.ForeignKey(Conceito, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Conceito")
    
    # Campos de frequência (RF1107)
    aulas_previstas = models.IntegerField(default=0, verbose_name="Quantidade de Aulas Previstas")
    aulas_lecionadas = models.IntegerField(default=0, verbose_name="Quantidade de Aulas Lecionadas")
    faltas = models.IntegerField(default=0, verbose_name="Número de Faltas")
    faltas_justificadas = models.IntegerField(default=0, verbose_name="Faltas Justificadas")
    
    # Controle
    tipo_lancamento = models.CharField(max_length=25, choices=TIPO_LANCAMENTO_CHOICES, verbose_name="Tipo de Lançamento")
    data_lancamento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Lançamento")
    usuario_lancamento = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Lançou")
    
    class Meta:
        verbose_name = "Lançamento de Nota/Frequência"
        verbose_name_plural = "Lançamentos de Notas/Frequência"
        unique_together = ['turma', 'disciplina', 'divisao_periodo', 'aluno']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.disciplina.nome} - {self.divisao_periodo.nome}"
    
    def get_frequencia_percentual(self):
        """Calcula percentual de frequência"""
        if self.aulas_lecionadas > 0:
            presencas = self.aulas_lecionadas - self.faltas
            return round((presencas / self.aulas_lecionadas) * 100, 2)
        return 0

class AtestadoMedico(models.Model):
    """Model para Atestados Médicos (RF1108)"""
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    
    # Dados do atestado (RF1108.1)
    data_atestado = models.DateField(verbose_name="Data do Atestado")
    numero_dias = models.IntegerField(verbose_name="Número de Dias")
    faltas_justificadas = models.IntegerField(verbose_name="Número de Faltas Justificadas")
    motivo = models.CharField(max_length=255, verbose_name="Motivo")
    descricao = models.TextField(verbose_name="Descrição")
    
    # Controle
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Cadastro")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Atestado Médico"
        verbose_name_plural = "Atestados Médicos"
        ordering = ['-data_atestado']
    
    def __str__(self):
        return f"Atestado - {self.aluno.nome} - {self.data_atestado.strftime('%d/%m/%Y')}"

class MediaGlobalConceito(models.Model):
    """Model para Lançamento de Média Global por Conceito (RF1201-RF1204)"""
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    conceito_global = models.ForeignKey(Conceito, on_delete=models.PROTECT, verbose_name="Conceito Global")
    
    # Dados calculados
    frequencia_percentual = models.DecimalField(
        max_digits=5, decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Frequência %"
    )
    total_faltas = models.IntegerField(default=0, verbose_name="Total de Faltas")
    
    # Controle
    data_lancamento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Lançamento")
    usuario_lancamento = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Lançou")
    
    class Meta:
        verbose_name = "Média Global por Conceito"
        verbose_name_plural = "Médias Globais por Conceito"
        unique_together = ['turma', 'aluno']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.conceito_global.nome}"

class RecuperacaoEspecial(models.Model):
    """Model para Recuperação Especial (RF1301-RF1305)"""
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, verbose_name="Disciplina")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    
    # Dados da recuperação
    nota_atual = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Nota Atual"
    )
    nota_recuperacao = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Nota da Recuperação"
    )
    nao_optou = models.BooleanField(default=False, verbose_name="Não Optou pela Recuperação")
    
    # Controle
    data_lancamento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Lançamento")
    usuario_lancamento = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Lançou")
    
    class Meta:
        verbose_name = "Recuperação Especial"
        verbose_name_plural = "Recuperações Especiais"
        unique_together = ['turma', 'disciplina', 'aluno']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.disciplina.nome} - Rec. Especial"

class HabilidadeCompetencia(models.Model):
    """Model para Habilidades e Competências (RF1401-RF1406)"""
    nome = models.CharField(max_length=255, verbose_name="Nome da Habilidade/Competência")
    descricao = models.TextField(verbose_name="Descrição")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, verbose_name="Disciplina")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Habilidade/Competência"
        verbose_name_plural = "Habilidades/Competências"
        ordering = ['disciplina', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.disciplina.nome})"

class ParecerDescritivo(models.Model):
    """Model para Parecer Descritivo (RF1401-RF1406)"""
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, verbose_name="Disciplina")
    divisao_periodo = models.ForeignKey(DivisaoPeriodoLetivo, on_delete=models.CASCADE, verbose_name="Divisão do Período")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    habilidade = models.ForeignKey(HabilidadeCompetencia, on_delete=models.CASCADE, verbose_name="Habilidade/Competência")
    
    # Avaliação da habilidade
    conceito = models.ForeignKey(Conceito, on_delete=models.PROTECT, verbose_name="Conceito")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    
    # Controle
    data_lancamento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Lançamento")
    usuario_lancamento = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Lançou")
    
    class Meta:
        verbose_name = "Parecer Descritivo"
        verbose_name_plural = "Pareceres Descritivos"
        unique_together = ['turma', 'disciplina', 'divisao_periodo', 'aluno', 'habilidade']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.habilidade.nome}"

class AvaliacaoDescritiva(models.Model):
    """Model para Avaliação Descritiva (RF1501-RF1503)"""
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    divisao_periodo = models.ForeignKey(DivisaoPeriodoLetivo, on_delete=models.CASCADE, verbose_name="Divisão do Período")
    
    # Campos opcionais baseados na configuração da matriz curricular
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Disciplina")
    
    # Conteúdo da avaliação
    observacoes_descricao_global = models.TextField(verbose_name="Observações / Descrição Global")
    
    # Controle
    data_lancamento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Lançamento")
    usuario_lancamento = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Lançou")
    
    class Meta:
        verbose_name = "Avaliação Descritiva"
        verbose_name_plural = "Avaliações Descritivas"
        unique_together = ['turma', 'aluno', 'divisao_periodo', 'disciplina']
    
    def __str__(self):
        disciplina_str = f" - {self.disciplina.nome}" if self.disciplina else ""
        return f"{self.aluno.nome} - {self.divisao_periodo.nome}{disciplina_str}"

class PendenciaAvaliacao(models.Model):
    """Model para Pendências de Avaliação (RF1601-RF1604)"""
    TIPO_PENDENCIA_CHOICES = [
        ('NOTA_NAO_INFORMADA', 'Nota não informada'),
        ('FREQUENCIA_NAO_INFORMADA', 'Frequência não informada'),
        ('CONCEITO_NAO_INFORMADO', 'Conceito não informado'),
        ('PARECER_NAO_INFORMADO', 'Parecer não informado'),
    ]
    
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, verbose_name="Disciplina")
    divisao_periodo = models.ForeignKey(DivisaoPeriodoLetivo, on_delete=models.CASCADE, verbose_name="Divisão do Período")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    
    tipo_pendencia = models.CharField(max_length=30, choices=TIPO_PENDENCIA_CHOICES, verbose_name="Tipo de Pendência")
    resolvida = models.BooleanField(default=False, verbose_name="Pendência Resolvida")
    
    # Controle
    data_identificacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Identificação")
    data_resolucao = models.DateTimeField(blank=True, null=True, verbose_name="Data de Resolução")
    usuario_resolucao = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Usuário que Resolveu")
    
    class Meta:
        verbose_name = "Pendência de Avaliação"
        verbose_name_plural = "Pendências de Avaliação"
        unique_together = ['turma', 'disciplina', 'divisao_periodo', 'aluno', 'tipo_pendencia']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.get_tipo_pendencia_display()}"

class DiarioOnline(models.Model):
    """Model para registro de acesso ao Diário Online (RF1701-RF1706)"""
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, verbose_name="Disciplina")
    divisao_periodo = models.ForeignKey(DivisaoPeriodoLetivo, on_delete=models.CASCADE, verbose_name="Divisão do Período")
    professor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Professor")
    
    # Controle de acesso
    data_acesso = models.DateTimeField(auto_now_add=True, verbose_name="Data de Acesso")
    ultima_atividade = models.DateTimeField(auto_now=True, verbose_name="Última Atividade")
    
    class Meta:
        verbose_name = "Acesso ao Diário Online"
        verbose_name_plural = "Acessos ao Diário Online"
        unique_together = ['turma', 'disciplina', 'divisao_periodo', 'professor']
    
    def __str__(self):
        return f"{self.professor.get_full_name()} - {self.turma.nome} - {self.disciplina.nome}"

class ConteudoAula(models.Model):
    """Model para Conteúdo/Matéria das Aulas (RF1706)"""
    diario = models.ForeignKey(DiarioOnline, on_delete=models.CASCADE, related_name='conteudos', verbose_name="Diário")
    data_aula = models.DateField(verbose_name="Data da Aula")
    conteudo_lecionado = models.TextField(verbose_name="Conteúdo/Matéria Lecionada")
    modulo_registrado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Módulo Registrado")
    
    # Controle
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Registro")
    usuario_registro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Registrou")
    
    class Meta:
        verbose_name = "Conteúdo de Aula"
        verbose_name_plural = "Conteúdos de Aulas"
        unique_together = ['diario', 'data_aula']
        ordering = ['-data_aula']
    
    def __str__(self):
        return f"{self.data_aula.strftime('%d/%m/%Y')} - {self.diario.disciplina.nome}"

class Enturmacao(models.Model):
    """Model para Enturmação de Alunos"""
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='enturmacoes', verbose_name="Turma")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='enturmacoes', verbose_name="Aluno")
    data_enturmacao = models.DateField(auto_now_add=True, verbose_name="Data de Enturmação")
    ativo = models.BooleanField(default=True, verbose_name="Enturmação Ativa")
    data_desenturmacao = models.DateField(blank=True, null=True, verbose_name="Data de Desenturmação")
    motivo_desenturmacao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Motivo da Desenturmação")
    
    # Controle
    usuario_enturmacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Enturmou")
    usuario_desenturmacao = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True, 
        related_name='desenturmacoes', verbose_name="Usuário que Desenturmou"
    )
    
    class Meta:
        verbose_name = "Enturmação"
        verbose_name_plural = "Enturmações"
        unique_together = ['turma', 'aluno', 'ativo']
        ordering = ['turma', 'aluno__nome']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.turma.nome}"
