from django.db import models
from django.contrib.auth.models import User


class DiarioEletronico(models.Model):
    """Model para Diário Eletrônico - criado automaticamente para cada turma/disciplina"""
    turma = models.ForeignKey('turma.Turma', on_delete=models.CASCADE, related_name='diarios', verbose_name="Turma")
    disciplina = models.ForeignKey('turma.Disciplina', on_delete=models.CASCADE, verbose_name="Disciplina")
    periodo_letivo = models.CharField(max_length=4, verbose_name="Período Letivo", blank=True, null=True)
    professor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Professor Responsável", null=True, blank=True)
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
        unique_together = ['turma', 'disciplina', 'periodo_letivo']
        ordering = ['turma__nome', 'disciplina__nome']

    def __str__(self):
        return f"{self.turma.nome} - {self.disciplina.nome} ({self.periodo_letivo})"

    def get_alunos(self):
        """Retorna alunos do diário (alunos enturmados)"""
        return self.turma.get_alunos_enturmados()
