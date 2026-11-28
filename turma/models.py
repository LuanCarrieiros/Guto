from datetime import date

from django.db import models
from django.db.models.functions import Lower
from guto_system.utils import ano_atual
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
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

class Turma(models.Model):
    """Model para Turmas"""
    TIPO_ENSINO_CHOICES = [
        ('EDUCACAO_INFANTIL', 'Educação Infantil'),
        ('ENSINO_FUNDAMENTAL_I', 'Ensino Fundamental I'),
        ('ENSINO_FUNDAMENTAL_II', 'Ensino Fundamental II'),
        ('ENSINO_MEDIO', 'Ensino Médio'),
    ]
    
    # Choices organizados por nível de ensino
    ANO_SERIE_CHOICES = [
        # Educação Infantil
        ('BERÇARIO', 'Berçário'),
        ('MATERNAL_I', 'Maternal I'),
        ('MATERNAL_II', 'Maternal II'),
        ('PRE_I', 'Pré I'),
        ('PRE_II', 'Pré II'),
        # Ensino Fundamental I (1º ao 5º ano)
        ('1_ANO', '1º Ano'),
        ('2_ANO', '2º Ano'),
        ('3_ANO', '3º Ano'),
        ('4_ANO', '4º Ano'),
        ('5_ANO', '5º Ano'),
        # Ensino Fundamental II (6º ao 9º ano)
        ('6_ANO', '6º Ano'),
        ('7_ANO', '7º Ano'),
        ('8_ANO', '8º Ano'),
        ('9_ANO', '9º Ano'),
        # Ensino Médio (1º ao 3º ano)
        ('1_ANO_EM', '1º Ano'),
        ('2_ANO_EM', '2º Ano'),
        ('3_ANO_EM', '3º Ano'),
    ]
    
    TURNO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
        ('NOTURNO', 'Noturno'),
        ('INTEGRAL', 'Integral'),
    ]
    
    nome = models.CharField(max_length=255, verbose_name="Nome da Turma")
    periodo_letivo = models.CharField(max_length=4, default=ano_atual, verbose_name="Período Letivo")
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
        return f"{self.nome} · {self.get_ano_serie_display()} · {self.get_turno_display()} ({self.periodo_letivo})"
    
    def get_total_alunos(self):
        """Retorna total de alunos enturmados"""
        return self.enturmacoes.filter(ativo=True).count()
    
    def get_vagas_disponiveis(self):
        """Retorna número de vagas disponíveis"""
        return self.vagas_total - self.get_total_alunos()
    
    def get_alunos_enturmados(self):
        """Retorna queryset dos alunos enturmados na turma"""
        from alunos.models import Aluno
        return Aluno.objects.filter(
            enturmacoes__turma=self,
            enturmacoes__ativo=True
        ).select_related('usuario_cadastro', 'documentacao', 'transporte').order_by('nome')
    
    def get_percentual_ocupacao(self):
        """Retorna o percentual de ocupação da turma"""
        if self.vagas_total == 0:
            return 0
        return round((self.get_total_alunos() * 100) / self.vagas_total)

    def get_disciplinas(self):
        """Disciplinas da turma no diário (vinculadas em "Gerenciar disciplinas").
        Se a turma ainda não tiver disciplinas vinculadas, retorna todas as ativas."""
        vinculadas = Disciplina.objects.filter(
            ativo=True, diarioeletronico__turma=self, diarioeletronico__ativo=True
        ).distinct().order_by('nome')
        return vinculadas if vinculadas.exists() else Disciplina.objects.filter(ativo=True).order_by('nome')
    
    @classmethod
    def get_anos_series_por_tipo(cls, tipo_ensino):
        """Retorna as opções de ano/série filtradas por tipo de ensino"""
        if tipo_ensino == 'EDUCACAO_INFANTIL':
            return [('BERÇARIO', 'Berçário'), ('MATERNAL_I', 'Maternal I'), 
                   ('MATERNAL_II', 'Maternal II'), ('PRE_I', 'Pré I'), ('PRE_II', 'Pré II')]
        elif tipo_ensino == 'ENSINO_FUNDAMENTAL_I':
            return [('1_ANO', '1º Ano'), ('2_ANO', '2º Ano'), ('3_ANO', '3º Ano'), 
                   ('4_ANO', '4º Ano'), ('5_ANO', '5º Ano')]
        elif tipo_ensino == 'ENSINO_FUNDAMENTAL_II':
            return [('6_ANO', '6º Ano'), ('7_ANO', '7º Ano'), ('8_ANO', '8º Ano'), 
                   ('9_ANO', '9º Ano')]
        elif tipo_ensino == 'ENSINO_MEDIO':
            return [('1_ANO_EM', '1º Ano'), ('2_ANO_EM', '2º Ano'), ('3_ANO_EM', '3º Ano')]
        else:
            return []  # Retorna lista vazia para tipos inválidos


class Disciplina(models.Model):
    """Model para Disciplinas"""
    nome = models.CharField(max_length=255, verbose_name="Nome da Disciplina")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código da Disciplina", blank=True)
    avalia_por_conceito = models.BooleanField(default=False, verbose_name="Avalia por Conceito")
    carga_horaria = models.IntegerField(default=40, verbose_name="Carga Horária")
    ativo = models.BooleanField(default=True, verbose_name="Disciplina Ativa")

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        ordering = ['nome']
        constraints = [
            # Sem duplicatas que diferem só em maiúsculas/minúsculas (ex.: "Matemática" e "MATEMÁTICA")
            models.UniqueConstraint(Lower('nome'), name='disciplina_nome_unico'),
        ]

    def save(self, *args, **kwargs):
        """Gera código automático se não fornecido"""
        if not self.codigo:
            self.codigo = self.gerar_codigo_automatico()
        super().save(*args, **kwargs)

    def gerar_codigo_automatico(self):
        """Gera código estiloso baseado no nome da disciplina"""
        import re

        # Remover acentos e caracteres especiais
        nome_limpo = self.nome.upper()
        nome_limpo = re.sub(r'[ÁÀÂÃÄ]', 'A', nome_limpo)
        nome_limpo = re.sub(r'[ÉÈÊË]', 'E', nome_limpo)
        nome_limpo = re.sub(r'[ÍÌÎÏ]', 'I', nome_limpo)
        nome_limpo = re.sub(r'[ÓÒÔÕÖ]', 'O', nome_limpo)
        nome_limpo = re.sub(r'[ÚÙÛÜ]', 'U', nome_limpo)
        nome_limpo = re.sub(r'[ÇC]', 'C', nome_limpo)
        nome_limpo = re.sub(r'[^A-Z\s]', '', nome_limpo)

        # Mapeamento de disciplinas comuns para códigos estilosos
        codigos_especiais = {
            'MATEMATICA': 'MAT',
            'PORTUGUES': 'PORT',
            'LINGUA PORTUGUESA': 'PORT',
            'HISTORIA': 'HIST',
            'GEOGRAFIA': 'GEO',
            'CIENCIAS': 'CIEN',
            'BIOLOGIA': 'BIO',
            'FISICA': 'FIS',
            'QUIMICA': 'QUIM',
            'FILOSOFIA': 'FIL',
            'SOCIOLOGIA': 'SOC',
            'EDUCACAO FISICA': 'EDFIS',
            'ARTES': 'ART',
            'INGLES': 'ING',
            'ESPANHOL': 'ESP',
            'INFORMATICA': 'INFO',
            'LITERATURA': 'LIT',
            'REDACAO': 'RED',
            'GEOMETRIA': 'GEOM',
            'ALGEBRA': 'ALG',
            'ENSINO RELIGIOSO': 'ENS_REL'
        }

        # Verificar se é uma disciplina especial
        for disciplina_key, codigo_base in codigos_especiais.items():
            if disciplina_key in nome_limpo:
                # Gerar número sequencial
                contador = 1
                while True:
                    codigo_proposto = f"{codigo_base}{contador:03d}"
                    if not Disciplina.objects.filter(codigo=codigo_proposto).exists():
                        return codigo_proposto
                    contador += 1

        # Para disciplinas não mapeadas, usar primeiras letras
        palavras = nome_limpo.split()
        if len(palavras) >= 2:
            # Pegar primeiras 2-3 letras das principais palavras
            codigo_base = ''.join([palavra[:2] for palavra in palavras[:2]])
        else:
            # Uma palavra só, pegar primeiras 3-4 letras
            codigo_base = palavras[0][:4] if len(palavras[0]) >= 4 else palavras[0]

        # Gerar número sequencial
        contador = 1
        while True:
            codigo_proposto = f"{codigo_base}{contador:03d}"
            if not Disciplina.objects.filter(codigo=codigo_proposto).exists():
                return codigo_proposto
            contador += 1

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
        ordering = ['turma', 'aluno__nome']
        constraints = [
            # RN-ENT001: um aluno só pode estar ativo em uma turma por vez.
            # As enturmações encerradas ficam como histórico (quantas forem).
            models.UniqueConstraint(
                fields=['aluno'], condition=models.Q(ativo=True), name='enturmacao_um_ativo_por_aluno',
            ),
        ]

    def __str__(self):
        return f"{self.aluno.nome} - {self.turma.nome}"

    def encerrar(self, usuario, motivo=''):
        """Encerra a enturmação mantendo o registro no histórico do aluno."""
        self.ativo = False
        self.data_desenturmacao = date.today()
        self.motivo_desenturmacao = motivo or None
        self.usuario_desenturmacao = usuario
        self.save()

    @classmethod
    def enturmar(cls, turma, aluno, usuario):
        """
        Enturma o aluno na turma. Se ele estiver ativo em outra turma, aquela
        enturmação é encerrada como transferência (RN-ENT002). Retorna a enturmação ativa.
        """
        atual = cls.objects.filter(aluno=aluno, ativo=True).select_related('turma').first()
        if atual and atual.turma_id == turma.pk:
            return atual
        if atual:
            atual.encerrar(usuario, f'Transferido para {turma}')
        return cls.objects.create(turma=turma, aluno=aluno, ativo=True, usuario_enturmacao=usuario)


class AulaRegistrada(models.Model):
    """Model para registro de aulas ministradas"""
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='aulas', verbose_name="Turma")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, verbose_name="Disciplina")
    professor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Professor")

    # Dados da aula
    data_aula = models.DateField(verbose_name="Data da Aula")
    horario_inicio = models.TimeField(verbose_name="Horário de Início")
    horario_fim = models.TimeField(verbose_name="Horário de Fim")
    conteudo_programatico = models.TextField(verbose_name="Conteúdo Programático")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    # Controle
    chamada_realizada = models.BooleanField(default=False, verbose_name="Chamada Realizada")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Registro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Aula Registrada"
        verbose_name_plural = "Aulas Registradas"
        unique_together = ['turma', 'disciplina', 'data_aula', 'horario_inicio']
        ordering = ['-data_aula', 'horario_inicio']

    def __str__(self):
        return f"{self.disciplina.nome} - {self.turma.nome} - {self.data_aula.strftime('%d/%m/%Y')}"


class RegistroFrequencia(models.Model):
    """Model para registro de frequência por aula"""
    SITUACAO_CHOICES = [
        ('PRESENTE', 'Presente'),
        ('AUSENTE', 'Ausente'),
        ('JUSTIFICADO', 'Ausente Justificado'),
        ('ATRASADO', 'Atrasado'),
    ]

    aula = models.ForeignKey(AulaRegistrada, on_delete=models.CASCADE, related_name='frequencias', verbose_name="Aula")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    situacao = models.CharField(max_length=15, choices=SITUACAO_CHOICES, default='PRESENTE', verbose_name="Situação")
    observacoes = models.CharField(max_length=255, blank=True, null=True, verbose_name="Observações")

    # Controle
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Registro")
    usuario_registro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Registrado por")

    class Meta:
        verbose_name = "Registro de Frequência"
        verbose_name_plural = "Registros de Frequência"
        unique_together = ['aula', 'aluno']
        ordering = ['aluno__nome']

    def __str__(self):
        return f"{self.aluno.nome} - {self.get_situacao_display()} - {self.aula.data_aula.strftime('%d/%m/%Y')}"


class TipoAvaliacao(models.Model):
    """Model para tipos de avaliação (Prova, Trabalho, Participação, etc.)"""
    nome = models.CharField(max_length=100, verbose_name="Nome do Tipo")
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição")
    peso_default = models.DecimalField(max_digits=3, decimal_places=1, default=1.0, verbose_name="Peso Padrão")
    cor_display = models.CharField(max_length=7, default='#3B82F6', verbose_name="Cor para Exibição")
    ativo = models.BooleanField(default=True, verbose_name="Tipo Ativo")

    class Meta:
        verbose_name = "Tipo de Avaliação"
        verbose_name_plural = "Tipos de Avaliação"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Avaliacao(models.Model):
    """Model para avaliações aplicadas"""
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='avaliacoes', verbose_name="Turma")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, verbose_name="Disciplina")
    divisao_periodo = models.ForeignKey(DivisaoPeriodoLetivo, on_delete=models.CASCADE, verbose_name="Período")
    tipo_avaliacao = models.ForeignKey(TipoAvaliacao, on_delete=models.CASCADE, verbose_name="Tipo de Avaliação")
    professor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Professor")

    # Dados da avaliação
    nome = models.CharField(max_length=255, verbose_name="Nome da Avaliação")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    data_aplicacao = models.DateField(verbose_name="Data de Aplicação")
    valor_maximo = models.DecimalField(max_digits=4, decimal_places=2, default=10.00, verbose_name="Valor Máximo")
    peso = models.DecimalField(max_digits=3, decimal_places=1, default=1.0, verbose_name="Peso")

    # Controle
    ativo = models.BooleanField(default=True, verbose_name="Avaliação Ativa")
    notas_lancadas = models.BooleanField(default=False, verbose_name="Notas Lançadas")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        ordering = ['-data_aplicacao', 'nome']

    def __str__(self):
        return f"{self.nome} - {self.turma.nome} - {self.disciplina.nome}"


class NotaAvaliacao(models.Model):
    """Model para notas individuais de avaliações"""
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name='notas', verbose_name="Avaliação")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    nota = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name="Nota"
    )
    conceito = models.ForeignKey(Conceito, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Conceito")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    # Status
    ausente = models.BooleanField(default=False, verbose_name="Ausente na Avaliação")
    dispensado = models.BooleanField(default=False, verbose_name="Dispensado da Avaliação")

    # Controle
    data_lancamento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Lançamento")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_lancamento = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Lançado por")

    class Meta:
        verbose_name = "Nota de Avaliação"
        verbose_name_plural = "Notas de Avaliações"
        unique_together = ['avaliacao', 'aluno']
        ordering = ['aluno__nome']

    @property
    def turma(self):
        return self.avaliacao.turma

    @property
    def disciplina(self):
        return self.avaliacao.disciplina

    def __str__(self):
        return f"{self.aluno.nome} - {self.avaliacao.nome}: {self.nota or self.conceito or 'N/A'}"
