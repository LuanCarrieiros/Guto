from django.db import models
from django.contrib.auth.models import User
from alunos.models import Aluno

class ItinerarioFormativo(models.Model):
    AREA_CONHECIMENTO_CHOICES = [
        ('LINGUAGENS', 'Linguagens e suas Tecnologias'),
        ('MATEMATICA', 'Matemática e suas Tecnologias'),
        ('NATUREZA', 'Ciências da Natureza e suas Tecnologias'),
        ('HUMANAS', 'Ciências Humanas e Sociais Aplicadas'),
        ('TECNICA', 'Formação Técnica e Profissional'),
    ]
    
    nome = models.CharField(max_length=255, verbose_name="Nome do Itinerário")
    carga_horaria_total = models.IntegerField(verbose_name="Carga Horária Total")
    areas_conhecimento = models.CharField(max_length=50, choices=AREA_CONHECIMENTO_CHOICES, verbose_name="Área de Conhecimento")
    habilidades = models.TextField(verbose_name="Habilidades")
    vagas_disponiveis = models.IntegerField(default=30, verbose_name="Vagas Disponíveis")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True)
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = "Itinerário Formativo"
        verbose_name_plural = "Itinerários Formativos"
        
    def __str__(self):
        return self.nome

class UnidadeCurricular(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome da Unidade")
    carga_horaria = models.IntegerField(verbose_name="Carga Horária")
    ementa = models.TextField(verbose_name="Ementa")
    habilidades_especificas = models.TextField(verbose_name="Habilidades Específicas")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True)
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = "Unidade Curricular"
        verbose_name_plural = "Unidades Curriculares"
        
    def __str__(self):
        return self.nome

class AssociacaoItinerarioUnidade(models.Model):
    itinerario = models.ForeignKey(ItinerarioFormativo, on_delete=models.CASCADE, related_name='unidades')
    unidade = models.ForeignKey(UnidadeCurricular, on_delete=models.CASCADE)
    ordem = models.IntegerField(default=1, verbose_name="Ordem na Grade")
    
    class Meta:
        verbose_name = "Associação Itinerário-Unidade"
        verbose_name_plural = "Associações Itinerário-Unidade"
        unique_together = ['itinerario', 'unidade']

class EnturmacaoItinerario(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='itinerarios')
    itinerario = models.ForeignKey(ItinerarioFormativo, on_delete=models.CASCADE, related_name='alunos')
    data_enturmacao = models.DateTimeField(auto_now_add=True)
    usuario_enturmacao = models.ForeignKey(User, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = "Enturmação em Itinerário"
        verbose_name_plural = "Enturmações em Itinerários"
        unique_together = ['aluno', 'itinerario']
