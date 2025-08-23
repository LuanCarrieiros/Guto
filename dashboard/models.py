from django.db import models
from django.contrib.auth.models import User

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


class AtividadeRecente(models.Model):
    TIPO_ACAO_CHOICES = [
        ('CRIAR', 'Criou'),
        ('EDITAR', 'Editou'),
        ('DELETAR', 'Deletou'),
        ('VISUALIZAR', 'Visualizou'),
    ]
    
    MODULO_CHOICES = [
        ('ALUNOS', 'Alunos'),
        ('FUNCIONARIOS', 'Funcionários'),
        ('OPCOES', 'Opções'),
        ('AEE', 'AEE/AC'),
        ('AVALIACAO', 'Avaliação'),
        ('UTILITARIOS', 'Utilitários'),
        ('DASHBOARD', 'Dashboard'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    acao = models.CharField(max_length=20, choices=TIPO_ACAO_CHOICES, verbose_name="Ação")
    modulo = models.CharField(max_length=20, choices=MODULO_CHOICES, verbose_name="Módulo")
    objeto_nome = models.CharField(max_length=255, verbose_name="Nome do Objeto")
    objeto_id = models.IntegerField(null=True, blank=True, verbose_name="ID do Objeto")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    data_atividade = models.DateTimeField(auto_now_add=True, verbose_name="Data da Atividade")
    
    class Meta:
        verbose_name = "Atividade Recente"
        verbose_name_plural = "Atividades Recentes"
        ordering = ['-data_atividade']
    
    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} {self.get_acao_display().lower()} {self.objeto_nome}"
    
    @property
    def icone(self):
        icones = {
            'ALUNOS': 'fas fa-user-graduate',
            'FUNCIONARIOS': 'fas fa-users',
            'OPCOES': 'fas fa-cog',
            'AEE': 'fas fa-hands-helping',
            'AVALIACAO': 'fas fa-clipboard-list',
            'UTILITARIOS': 'fas fa-tools',
            'DASHBOARD': 'fas fa-tachometer-alt',
        }
        return icones.get(self.modulo, 'fas fa-file')
    
    @property
    def cor(self):
        cores = {
            'ALUNOS': 'text-blue-600',
            'FUNCIONARIOS': 'text-green-600',
            'OPCOES': 'text-indigo-600',
            'AEE': 'text-pink-600',
            'AVALIACAO': 'text-yellow-600',
            'UTILITARIOS': 'text-teal-600',
            'DASHBOARD': 'text-gray-600',
        }
        return cores.get(self.modulo, 'text-gray-600')
    
    @classmethod
    def registrar_atividade(cls, usuario, acao, modulo, objeto_nome, objeto_id=None, descricao=None):
        """Método helper para registrar uma nova atividade"""
        return cls.objects.create(
            usuario=usuario,
            acao=acao,
            modulo=modulo,
            objeto_nome=objeto_nome,
            objeto_id=objeto_id,
            descricao=descricao
        )
