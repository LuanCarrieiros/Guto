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
        from alunos.models import Aluno
        return Aluno.objects.filter(
            enturmacoes__turma=self,
            enturmacoes__ativo=True
        ).select_related('usuario_cadastro', 'documentacao', 'transporte')
    
    def get_percentual_ocupacao(self):
        """Retorna o percentual de ocupação da turma"""
        if self.vagas_total == 0:
            return 0
        return round((self.get_total_alunos() * 100) / self.vagas_total)

    def get_disciplinas(self):
        """Retorna todas as disciplinas ativas disponíveis para uso no diário"""
        return Disciplina.objects.filter(ativo=True).order_by('nome')
    
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
    
    def criar_diario_automatico(self):
        """Cria diário automático para a turma com todas as disciplinas ativas"""
        from django.db import transaction
        
        with transaction.atomic():
            # Buscar ou criar divisão período padrão
            divisao_periodo, created = DivisaoPeriodoLetivo.objects.get_or_create(
                nome="1º Bimestre",
                periodo_letivo=self.periodo_letivo,
                defaults={
                    'tipo_divisao': 'BIMESTRE',
                    'ordem': 1,
                    'data_inicio': f'{self.periodo_letivo}-01-01',
                    'data_fim': f'{self.periodo_letivo}-03-31',
                    'ativo': True
                }
            )
            
            # Criar diários para todas as disciplinas ativas
            from diario.models import DiarioEletronico
            disciplinas = Disciplina.objects.filter(ativo=True)
            for disciplina in disciplinas:
                DiarioEletronico.objects.get_or_create(
                    turma=self,
                    disciplina=disciplina,
                    periodo_letivo=self.periodo_letivo,
                    defaults={
                        'ativo': True
                    }
                )

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
        unique_together = ['aluno', 'ativo']
        ordering = ['turma', 'aluno__nome']

    def __str__(self):
        return f"{self.aluno.nome} - {self.turma.nome}"


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

    def __str__(self):
        return f"{self.aluno.nome} - {self.avaliacao.nome}: {self.nota or self.conceito or 'N/A'}"

