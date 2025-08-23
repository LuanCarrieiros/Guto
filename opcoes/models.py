from django.db import models
from django.contrib.auth.models import User
from datetime import date

class TipoRelatorio(models.Model):
    """Model para os tipos de relatórios disponíveis (RF605)"""
    TIPOS_RELATORIO = [
        ('FICHA_MATRICULA', 'Ficha de Matrícula'),
        ('BOLETIM', 'Boletim'),
        ('FICHA_INDIVIDUAL', 'Ficha Individual'),
        ('DIAGNOSTICO_HABILIDADES', 'Diagnóstico de Habilidades'),
    ]
    
    nome = models.CharField(max_length=100, choices=TIPOS_RELATORIO, unique=True, verbose_name="Nome do Relatório")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Relatório Ativo")
    
    class Meta:
        verbose_name = "Tipo de Relatório"
        verbose_name_plural = "Tipos de Relatórios"
        ordering = ['nome']
    
    def __str__(self):
        return dict(self.TIPOS_RELATORIO)[self.nome]

class FiltroRelatorio(models.Model):
    """Model para armazenar filtros aplicados aos relatórios (RF607)"""
    STATUS_DIARIO_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('FECHADO', 'Fechado'),
        ('TODOS', 'Todos'),
    ]
    
    SITUACAO_TURMA_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('ENCERRADO', 'Encerrado'),
        ('TODOS', 'Todos'),
    ]
    
    TIPO_ENSINO_CHOICES = [
        ('INFANTIL', 'Educação Infantil'),
        ('FUNDAMENTAL_I', 'Ensino Fundamental I'),
        ('FUNDAMENTAL_II', 'Ensino Fundamental II'),
        ('MEDIO', 'Ensino Médio'),
        ('EJA', 'Educação de Jovens e Adultos'),
        ('ESPECIAL', 'Educação Especial'),
        ('TODOS', 'Todos'),
    ]
    
    TURNO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
        ('NOTURNO', 'Noturno'),
        ('INTEGRAL', 'Integral'),
        ('TODOS', 'Todos'),
    ]
    
    tipo_relatorio = models.ForeignKey(TipoRelatorio, on_delete=models.CASCADE, verbose_name="Tipo de Relatório")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    
    # Filtros obrigatórios (RF607)
    periodo_letivo = models.CharField(max_length=4, default=str(date.today().year), verbose_name="Período Letivo")
    tipo_ensino = models.CharField(max_length=20, choices=TIPO_ENSINO_CHOICES, default='TODOS', verbose_name="Tipo de Ensino")
    ano_serie = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ano/Série/Módulo/Etapa")
    turno = models.CharField(max_length=15, choices=TURNO_CHOICES, default='TODOS', verbose_name="Turno")
    status_diario = models.CharField(max_length=10, choices=STATUS_DIARIO_CHOICES, default='TODOS', verbose_name="Status do Diário")
    situacao_turma = models.CharField(max_length=15, choices=SITUACAO_TURMA_CHOICES, default='TODOS', verbose_name="Situação da Turma")
    
    data_filtro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Filtro")
    
    class Meta:
        verbose_name = "Filtro de Relatório"
        verbose_name_plural = "Filtros de Relatórios"
        ordering = ['-data_filtro']

class CalendarioEscolar(models.Model):
    """Model para o calendário escolar (RF702-RF704)"""
    TIPO_ENSINO_CHOICES = [
        ('INFANTIL', 'Educação Infantil'),
        ('FUNDAMENTAL_I', 'Ensino Fundamental I'),
        ('FUNDAMENTAL_II', 'Ensino Fundamental II'),
        ('MEDIO', 'Ensino Médio'),
        ('EJA', 'Educação de Jovens e Adultos'),
        ('ESPECIAL', 'Educação Especial'),
    ]
    
    TURNO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
        ('NOTURNO', 'Noturno'),
        ('INTEGRAL', 'Integral'),
    ]
    
    SERIE_CHOICES = [
        ('1_ANO', '1º Ano'),
        ('2_ANO', '2º Ano'),
        ('3_ANO', '3º Ano'),
        ('4_ANO', '4º Ano'),
        ('5_ANO', '5º Ano'),
        ('6_ANO', '6º Ano'),
        ('7_ANO', '7º Ano'),
        ('8_ANO', '8º Ano'),
        ('9_ANO', '9º Ano'),
        ('1_MEDIO', '1º Ano - Ensino Médio'),
        ('2_MEDIO', '2º Ano - Ensino Médio'),
        ('3_MEDIO', '3º Ano - Ensino Médio'),
        ('MULTI', 'Multisseriada'),
    ]
    
    # Campos obrigatórios (RF704)
    periodo_letivo = models.CharField(max_length=4, default=str(date.today().year), verbose_name="Período Letivo")
    tipo_ensino = models.CharField(max_length=20, choices=TIPO_ENSINO_CHOICES, verbose_name="Tipo de Ensino")
    serie = models.CharField(max_length=15, choices=SERIE_CHOICES, verbose_name="Série")
    turno = models.CharField(max_length=15, choices=TURNO_CHOICES, verbose_name="Turno")
    
    # Dados do calendário
    data_inicio_letivo = models.DateField(verbose_name="Início do Ano Letivo")
    data_fim_letivo = models.DateField(verbose_name="Fim do Ano Letivo")
    dias_letivos = models.IntegerField(default=200, verbose_name="Dias Letivos")
    dias_escolares = models.IntegerField(default=200, verbose_name="Dias Escolares")
    
    # Observações e detalhes
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Controle
    ativo = models.BooleanField(default=True, verbose_name="Calendário Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Criado por")
    
    class Meta:
        verbose_name = "Calendário Escolar"
        verbose_name_plural = "Calendários Escolares"
        ordering = ['-periodo_letivo', 'tipo_ensino', 'serie', 'turno']
        unique_together = ['periodo_letivo', 'tipo_ensino', 'serie', 'turno']
    
    def __str__(self):
        return f"{self.periodo_letivo} - {self.get_tipo_ensino_display()} - {self.get_serie_display()} - {self.get_turno_display()}"

class EventoCalendario(models.Model):
    """Model para eventos específicos do calendário"""
    TIPO_EVENTO_CHOICES = [
        ('AULA', 'Dia de Aula'),
        ('FERIADO', 'Feriado'),
        ('RECESSO', 'Recesso'),
        ('EVENTO_ESPECIAL', 'Evento Especial'),
        ('REUNIAO_PEDAGOGICA', 'Reunião Pedagógica'),
        ('FORMACAO', 'Formação/Capacitação'),
    ]
    
    calendario = models.ForeignKey(CalendarioEscolar, on_delete=models.CASCADE, related_name='eventos', verbose_name="Calendário")
    data_evento = models.DateField(verbose_name="Data do Evento")
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES, verbose_name="Tipo de Evento")
    nome_evento = models.CharField(max_length=255, verbose_name="Nome do Evento")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    dia_letivo = models.BooleanField(default=True, verbose_name="Conta como Dia Letivo")
    
    class Meta:
        verbose_name = "Evento do Calendário"
        verbose_name_plural = "Eventos do Calendário"
        ordering = ['data_evento']
        unique_together = ['calendario', 'data_evento', 'nome_evento']
    
    def __str__(self):
        return f"{self.data_evento.strftime('%d/%m/%Y')} - {self.nome_evento}"
