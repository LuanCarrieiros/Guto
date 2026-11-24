from django.db import models
from django.contrib.auth.models import User


class DiarioEletronico(models.Model):
    """
    Diário de uma disciplina em uma turma (ex.: Matemática do 1º A).
    Há um único diário por turma e disciplina; o professor responsável vem da
    associação de professores (Funcionários › Associação às Turmas).
    """
    turma = models.ForeignKey('turma.Turma', on_delete=models.CASCADE, related_name='diarios', verbose_name="Turma")
    disciplina = models.ForeignKey('turma.Disciplina', on_delete=models.CASCADE, verbose_name="Disciplina")
    ativo = models.BooleanField(default=True, verbose_name="Diário Ativo")

    # Controle de fechamento
    diario_fechado = models.BooleanField(default=False, verbose_name="Diário Fechado")
    data_fechamento = models.DateTimeField(null=True, blank=True, verbose_name="Data de Fechamento")
    usuario_fechamento = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='diarios_fechados', verbose_name="Usuário que Fechou")
    data_reabertura = models.DateTimeField(null=True, blank=True, verbose_name="Data de Reabertura")
    usuario_reabertura = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='diarios_reabertos', verbose_name="Usuário que Reabriu")

    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Diário Eletrônico"
        verbose_name_plural = "Diários Eletrônicos"
        unique_together = ['turma', 'disciplina']
        ordering = ['turma__nome', 'disciplina__nome']

    def __str__(self):
        return f"{self.turma.nome} - {self.disciplina.nome} ({self.turma.periodo_letivo})"

    @property
    def associacao_vigente(self):
        """Associação de professor em vigor para esta disciplina na turma (ou o regente da turma)."""
        from funcionarios.models import AssociacaoProfessor
        vigentes = AssociacaoProfessor.objects.vigentes().filter(turma=self.turma).select_related('funcionario')
        return (vigentes.filter(disciplina=self.disciplina).first()
                or vigentes.filter(tipo_associacao='TURMA').first())

    @property
    def professor(self):
        associacao = self.associacao_vigente
        return associacao.funcionario if associacao else None
