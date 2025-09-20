from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from alunos.models import Aluno


class DiarioOnline(models.Model):
    """Model para registro de acesso ao Diário Online (RF1701-RF1706)"""
    turma = models.ForeignKey('turma.Turma', on_delete=models.CASCADE, verbose_name="Turma")
    disciplina = models.ForeignKey('turma.Disciplina', on_delete=models.CASCADE, verbose_name="Disciplina")
    divisao_periodo = models.ForeignKey('turma.DivisaoPeriodoLetivo', on_delete=models.CASCADE, verbose_name="Divisão do Período")
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


class DiarioEletronico(models.Model):
    """Model para Diário Eletrônico - criado automaticamente para cada turma/disciplina"""
    turma = models.ForeignKey('turma.Turma', on_delete=models.CASCADE, related_name='diarios', verbose_name="Turma")
    disciplina = models.ForeignKey('turma.Disciplina', on_delete=models.CASCADE, verbose_name="Disciplina")
    periodo_letivo = models.CharField(max_length=4, verbose_name="Período Letivo")
    ativo = models.BooleanField(default=True, verbose_name="Diário Ativo")

    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Diário Eletrônico"
        verbose_name_plural = "Diários Eletrônicos"
        unique_together = ['turma', 'disciplina', 'periodo_letivo']
        ordering = ['turma__nome', 'disciplina__nome']

    def __str__(self):
        return f"{self.turma.nome} - {self.disciplina.nome} ({self.periodo_letivo})"

    def get_alunos(self):
        """Retorna alunos do diário (alunos enturmados)"""
        return self.turma.get_alunos_enturmados()


class RegistroChamada(models.Model):
    """Model para registro de chamada/frequência no diário eletrônico"""
    SITUACAO_CHOICES = [
        ('PRESENTE', 'Presente'),
        ('AUSENTE', 'Ausente'),
        ('JUSTIFICADO', 'Ausente Justificado'),
    ]

    diario = models.ForeignKey(DiarioEletronico, on_delete=models.CASCADE, related_name='chamadas', verbose_name="Diário")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    data_chamada = models.DateField(verbose_name="Data da Chamada")
    situacao = models.CharField(max_length=15, choices=SITUACAO_CHOICES, default='PRESENTE', verbose_name="Situação")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    # Controle
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Registro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_registro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Registrado por")

    class Meta:
        verbose_name = "Registro de Chamada"
        verbose_name_plural = "Registros de Chamada"
        unique_together = ['diario', 'aluno', 'data_chamada']
        ordering = ['data_chamada', 'aluno__nome']

    def __str__(self):
        return f"{self.aluno.nome} - {self.get_situacao_display()} - {self.data_chamada.strftime('%d/%m/%Y')}"


class RegistroNota(models.Model):
    """Model para registro de notas no diário eletrônico"""
    diario = models.ForeignKey(DiarioEletronico, on_delete=models.CASCADE, related_name='notas', verbose_name="Diário")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    divisao_periodo = models.ForeignKey('turma.DivisaoPeriodoLetivo', on_delete=models.CASCADE, verbose_name="Período")

    # Campos de avaliação
    nota = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Nota"
    )
    conceito = models.ForeignKey('turma.Conceito', on_delete=models.PROTECT, blank=True, null=True, verbose_name="Conceito")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    # Controle
    data_lancamento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Lançamento")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_lancamento = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Lançou")

    class Meta:
        verbose_name = "Registro de Nota"
        verbose_name_plural = "Registros de Notas"
        unique_together = ['diario', 'aluno', 'divisao_periodo']
        ordering = ['aluno__nome']

    def __str__(self):
        return f"{self.aluno.nome} - {self.diario.disciplina.nome} - {self.divisao_periodo.nome}"
