from django.db import models

class Funcionario(models.Model):
    codigo = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    data_admissao = models.DateField(verbose_name="Data de Admissão")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.codigo} - {self.nome} ({self.cargo})"

class Avaliacao(models.Model):
    titulo = models.CharField(max_length=255, verbose_name="Título")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    data_aplicacao = models.DateField(verbose_name="Data de Aplicação")
    pendente = models.BooleanField(default=True, verbose_name="Pendente")
    
    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        ordering = ['-data_aplicacao']
    
    def __str__(self):
        return self.titulo
