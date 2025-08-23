from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from alunos.models import Aluno

class ProjetoPedagogico(models.Model):
    """Model para Projetos Pedagógicos (RF806.2 - RNF801)"""
    TIPO_PROJETO_CHOICES = [
        ('AEE', 'Atendimento Educacional Especializado'),
        ('AC', 'Atividade Complementar'),
    ]
    
    nome = models.CharField(max_length=255, verbose_name="Nome do Projeto")
    tipo_projeto = models.CharField(max_length=10, choices=TIPO_PROJETO_CHOICES, verbose_name="Tipo de Projeto")
    periodo_letivo = models.CharField(max_length=4, default=str(date.today().year), verbose_name="Período Letivo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    carga_horaria = models.IntegerField(default=20, verbose_name="Carga Horária Semanal")
    ativo = models.BooleanField(default=True, verbose_name="Projeto Ativo")
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Criado por")
    
    class Meta:
        verbose_name = "Projeto Pedagógico"
        verbose_name_plural = "Projetos Pedagógicos"
        ordering = ['-periodo_letivo', 'tipo_projeto', 'nome']
        unique_together = ['nome', 'periodo_letivo']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_projeto_display()}) - {self.periodo_letivo}"

class TurmaAEE(models.Model):
    """Model para Turmas de AEE/Atividade Complementar (RF803-RF811)"""
    TURNO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
        ('NOTURNO', 'Noturno'),
        ('INTEGRAL', 'Integral'),
    ]
    
    SITUACAO_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('ENCERRADO', 'Encerrado'),
    ]
    
    ORDENACAO_CHOICES = [
        ('ALFABETICA', 'Alfabética'),
        ('DATA_NASCIMENTO', 'Data de Nascimento'),
        ('CODIGO', 'Código do Aluno'),
        ('PERSONALIZADA', 'Personalizada'),
    ]
    
    DIAS_SEMANA_CHOICES = [
        ('SEGUNDA', 'Segunda-feira'),
        ('TERCA', 'Terça-feira'),
        ('QUARTA', 'Quarta-feira'),
        ('QUINTA', 'Quinta-feira'),
        ('SEXTA', 'Sexta-feira'),
        ('SABADO', 'Sábado'),
    ]
    
    # Campos obrigatórios (RF806.1)
    nome = models.CharField(max_length=255, verbose_name="Nome da Turma")
    periodo_letivo = models.CharField(max_length=4, default=str(date.today().year), verbose_name="Período Letivo")
    turno = models.CharField(max_length=15, choices=TURNO_CHOICES, verbose_name="Turno")
    projeto_pedagogico = models.ForeignKey(ProjetoPedagogico, on_delete=models.PROTECT, verbose_name="Projeto Pedagógico")
    
    # Horários
    hora_inicio = models.TimeField(verbose_name="Hora de Início")
    hora_fim = models.TimeField(verbose_name="Hora de Término")
    
    # Configurações da turma
    maximo_alunos = models.IntegerField(
        default=20,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name="Número Máximo de Alunos"
    )
    ordenacao = models.CharField(max_length=20, choices=ORDENACAO_CHOICES, default='ALFABETICA', verbose_name="Ordenação")
    
    # Dias da semana (múltipla escolha usando campos boolean)
    segunda = models.BooleanField(default=False, verbose_name="Segunda-feira")
    terca = models.BooleanField(default=False, verbose_name="Terça-feira")
    quarta = models.BooleanField(default=False, verbose_name="Quarta-feira")
    quinta = models.BooleanField(default=False, verbose_name="Quinta-feira")
    sexta = models.BooleanField(default=False, verbose_name="Sexta-feira")
    sabado = models.BooleanField(default=False, verbose_name="Sábado")
    
    # Campos específicos para Atividade Complementar (RNF802)
    atividade_especifica = models.CharField(max_length=255, blank=True, null=True, verbose_name="Atividade Específica")
    local = models.CharField(max_length=255, blank=True, null=True, verbose_name="Local/Sala")
    material_necessario = models.TextField(blank=True, null=True, verbose_name="Material Necessário")
    
    # Status e controle
    situacao = models.CharField(max_length=15, choices=SITUACAO_CHOICES, default='ATIVO', verbose_name="Situação")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Dados de auditoria
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, related_name='turmas_aee_criadas', verbose_name="Criado por")
    
    class Meta:
        verbose_name = "Turma AEE/AC"
        verbose_name_plural = "Turmas AEE/AC"
        ordering = ['-periodo_letivo', 'turno', 'nome']
        unique_together = ['nome', 'periodo_letivo']
    
    def __str__(self):
        return f"{self.nome} - {self.get_turno_display()} ({self.periodo_letivo})"
    
    def get_dias_semana(self):
        """Retorna lista dos dias da semana que a turma funciona"""
        dias = []
        if self.segunda: dias.append('Segunda')
        if self.terca: dias.append('Terça')
        if self.quarta: dias.append('Quarta')
        if self.quinta: dias.append('Quinta')
        if self.sexta: dias.append('Sexta')
        if self.sabado: dias.append('Sábado')
        return ', '.join(dias)
    
    def get_total_alunos(self):
        """Retorna total de alunos enturmados"""
        return self.enturmacoes.filter(ativo=True).count()
    
    def tem_vaga(self):
        """Verifica se ainda há vagas na turma"""
        return self.get_total_alunos() < self.maximo_alunos

class EnturmacaoAEE(models.Model):
    """Model para controlar enturmação de alunos em turmas AEE/AC (RF901-RF908)"""
    ORIGEM_CHOICES = [
        ('PROPRIA_ESCOLA', 'Alunos da própria escola'),
        ('OUTRA_ESCOLA_REDE', 'Alunos de outra escola da rede municipal'),
        ('EXCLUSIVO_AEE', 'Alunos exclusivos de AEE/AC'),
    ]
    
    turma = models.ForeignKey(TurmaAEE, on_delete=models.CASCADE, related_name='enturmacoes', verbose_name="Turma")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='enturmacoes_aee', verbose_name="Aluno")
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, verbose_name="Origem do Aluno")
    
    # Dados específicos para alunos de outras escolas
    escola_origem = models.CharField(max_length=255, blank=True, null=True, verbose_name="Escola de Origem")
    codigo_escola_origem = models.CharField(max_length=20, blank=True, null=True, verbose_name="Código da Escola")
    
    # Dados para filtragem (RF904)
    ano_administrativo = models.CharField(max_length=4, verbose_name="Ano Administrativo")
    tipo_ensino = models.CharField(max_length=50, verbose_name="Tipo de Ensino")
    ano_serie = models.CharField(max_length=50, verbose_name="Ano/Série/Módulo/Etapa")
    
    # Status
    ativo = models.BooleanField(default=True, verbose_name="Enturmação Ativa")
    data_enturmacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Enturmação")
    data_saida = models.DateTimeField(blank=True, null=True, verbose_name="Data de Saída")
    usuario_enturmacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Enturmou")
    
    class Meta:
        verbose_name = "Enturmação AEE/AC"
        verbose_name_plural = "Enturmações AEE/AC"
        ordering = ['turma', 'aluno__nome']
        unique_together = ['turma', 'aluno', 'ativo']  # Um aluno só pode estar ativo em uma turma por vez
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.turma.nome}"

class HistoricoEnturmacao(models.Model):
    """Model para histórico de movimentações na enturmação"""
    ACAO_CHOICES = [
        ('ADICIONAR', 'Aluno Adicionado'),
        ('REMOVER', 'Aluno Removido'),
        ('REORDENAR', 'Lista Reordenada'),
    ]
    
    turma = models.ForeignKey(TurmaAEE, on_delete=models.CASCADE, related_name='historico', verbose_name="Turma")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Aluno")
    acao = models.CharField(max_length=15, choices=ACAO_CHOICES, verbose_name="Ação Realizada")
    data_acao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Ação")
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Histórico de Enturmação"
        verbose_name_plural = "Histórico de Enturmações"
        ordering = ['-data_acao']
    
    def __str__(self):
        if self.aluno:
            return f"{self.get_acao_display()} - {self.aluno.nome} em {self.turma.nome}"
        return f"{self.get_acao_display()} - {self.turma.nome}"

class AssociacaoEscola(models.Model):
    """Model para associar alunos de outras escolas à escola atual (RF1005)"""
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    escola_atual = models.CharField(max_length=255, verbose_name="Escola Atual")
    escola_origem = models.CharField(max_length=255, verbose_name="Escola de Origem")
    data_associacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Associação")
    usuario_associacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Associou")
    ativo = models.BooleanField(default=True, verbose_name="Associação Ativa")
    
    class Meta:
        verbose_name = "Associação de Escola"
        verbose_name_plural = "Associações de Escolas"
        unique_together = ['aluno', 'escola_atual']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.escola_origem} → {self.escola_atual}"
