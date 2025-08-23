from django.db import models
from django.contrib.auth.models import User
from alunos.models import Aluno
from funcionarios.models import Funcionario
from datetime import date

class ProgramaPedagogico(models.Model):
    TIPO_PROGRAMA_CHOICES = [
        ('REGULAR', 'Programa Regular'),
        ('REFORCO', 'Reforço Escolar'),
        ('ACELERACAO', 'Aceleração da Aprendizagem'),
        ('INCLUSAO', 'Educação Inclusiva'),
        ('EJAINTEGRADA', 'EJA Integrada'),
        ('PROFISSIONALIZANTE', 'Profissionalizante'),
        ('COMPLEMENTAR', 'Atividade Complementar'),
    ]
    
    MODALIDADE_CHOICES = [
        ('PRESENCIAL', 'Presencial'),
        ('SEMIPRESENCIAL', 'Semipresencial'),
        ('DISTANCIA', 'Educação à Distância'),
        ('HIBRIDA', 'Híbrida'),
    ]
    
    STATUS_CHOICES = [
        ('PLANEJAMENTO', 'Em Planejamento'),
        ('ATIVO', 'Ativo'),
        ('SUSPENSO', 'Suspenso'),
        ('ENCERRADO', 'Encerrado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    nome = models.CharField(max_length=255, verbose_name="Nome do Programa")
    descricao = models.TextField(verbose_name="Descrição do Programa")
    tipo_programa = models.CharField(max_length=20, choices=TIPO_PROGRAMA_CHOICES, verbose_name="Tipo de Programa")
    modalidade = models.CharField(max_length=20, choices=MODALIDADE_CHOICES, default='PRESENCIAL', verbose_name="Modalidade")
    
    # Período
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Término")
    carga_horaria_total = models.IntegerField(verbose_name="Carga Horária Total (horas)")
    
    # Objetivos e competências
    objetivos_gerais = models.TextField(verbose_name="Objetivos Gerais")
    objetivos_especificos = models.TextField(verbose_name="Objetivos Específicos")
    competencias = models.TextField(verbose_name="Competências Desenvolvidas")
    habilidades = models.TextField(verbose_name="Habilidades Trabalhadas")
    
    # Público-alvo
    publico_alvo = models.TextField(verbose_name="Público-Alvo")
    idade_minima = models.IntegerField(blank=True, null=True, verbose_name="Idade Mínima")
    idade_maxima = models.IntegerField(blank=True, null=True, verbose_name="Idade Máxima")
    vagas_disponiveis = models.IntegerField(default=30, verbose_name="Vagas Disponíveis")
    
    # Coordenação
    coordenador = models.ForeignKey(
        Funcionario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='programas_coordenados',
        verbose_name="Coordenador do Programa"
    )
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANEJAMENTO', verbose_name="Status")
    aprovado = models.BooleanField(default=False, verbose_name="Aprovado")
    data_aprovacao = models.DateField(blank=True, null=True, verbose_name="Data de Aprovação")
    
    # Recursos necessários
    recursos_humanos = models.TextField(blank=True, null=True, verbose_name="Recursos Humanos Necessários")
    recursos_materiais = models.TextField(blank=True, null=True, verbose_name="Recursos Materiais Necessários")
    recursos_tecnologicos = models.TextField(blank=True, null=True, verbose_name="Recursos Tecnológicos Necessários")
    
    # Avaliação
    metodologia_avaliacao = models.TextField(blank=True, null=True, verbose_name="Metodologia de Avaliação")
    criterios_aprovacao = models.TextField(blank=True, null=True, verbose_name="Critérios de Aprovação")
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Programa Pedagógico"
        verbose_name_plural = "Programas Pedagógicos"
        ordering = ['-data_inicio', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_programa_display()})"
    
    @property
    def dias_duracao(self):
        return (self.data_fim - self.data_inicio).days + 1
    
    @property
    def total_participantes(self):
        return self.participantes.filter(ativo=True).count()
    
    @property
    def vagas_restantes(self):
        return self.vagas_disponiveis - self.total_participantes
    
    @property
    def programa_em_andamento(self):
        today = date.today()
        return self.data_inicio <= today <= self.data_fim and self.status == 'ATIVO'

class ModuloPrograma(models.Model):
    programa = models.ForeignKey(ProgramaPedagogico, on_delete=models.CASCADE, related_name='modulos', verbose_name="Programa")
    nome = models.CharField(max_length=255, verbose_name="Nome do Módulo")
    descricao = models.TextField(verbose_name="Descrição do Módulo")
    ordem = models.IntegerField(default=1, verbose_name="Ordem no Programa")
    
    # Período
    data_inicio = models.DateField(verbose_name="Data de Início do Módulo")
    data_fim = models.DateField(verbose_name="Data de Término do Módulo")
    carga_horaria = models.IntegerField(verbose_name="Carga Horária (horas)")
    
    # Conteúdo
    conteudo_programatico = models.TextField(verbose_name="Conteúdo Programático")
    metodologia = models.TextField(verbose_name="Metodologia de Ensino")
    recursos_necessarios = models.TextField(blank=True, null=True, verbose_name="Recursos Necessários")
    
    # Professor responsável
    professor_responsavel = models.ForeignKey(
        Funcionario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='modulos_responsavel',
        verbose_name="Professor Responsável"
    )
    
    # Controle
    ativo = models.BooleanField(default=True, verbose_name="Módulo Ativo")
    
    class Meta:
        verbose_name = "Módulo do Programa"
        verbose_name_plural = "Módulos do Programa"
        ordering = ['programa', 'ordem']
        unique_together = ['programa', 'ordem']
    
    def __str__(self):
        return f"{self.programa.nome} - Módulo {self.ordem}: {self.nome}"
    
    @property
    def dias_duracao(self):
        return (self.data_fim - self.data_inicio).days + 1

class ParticipantePrograma(models.Model):
    SITUACAO_CHOICES = [
        ('INSCRITO', 'Inscrito'),
        ('ATIVO', 'Ativo'),
        ('SUSPENSO', 'Suspenso'),
        ('EVADIDO', 'Evadido'),
        ('CONCLUIDO', 'Concluído'),
        ('REPROVADO', 'Reprovado'),
    ]
    
    programa = models.ForeignKey(ProgramaPedagogico, on_delete=models.CASCADE, related_name='participantes', verbose_name="Programa")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='programas_participando', verbose_name="Aluno")
    
    # Controle
    data_inscricao = models.DateField(verbose_name="Data de Inscrição")
    data_inicio = models.DateField(blank=True, null=True, verbose_name="Data de Início")
    data_conclusao = models.DateField(blank=True, null=True, verbose_name="Data de Conclusão")
    situacao = models.CharField(max_length=20, choices=SITUACAO_CHOICES, default='INSCRITO', verbose_name="Situação")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Avaliação
    nota_final = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name="Nota Final")
    frequencia_total = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Frequência Total (%)")
    
    # Observações
    motivo_evasao = models.TextField(blank=True, null=True, verbose_name="Motivo da Evasão")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Participante do Programa"
        verbose_name_plural = "Participantes do Programa"
        unique_together = ['programa', 'aluno']
        ordering = ['programa', 'aluno__nome']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.programa.nome}"

class AulaPrograma(models.Model):
    TIPO_AULA_CHOICES = [
        ('TEORICA', 'Teórica'),
        ('PRATICA', 'Prática'),
        ('LABORATORIO', 'Laboratório'),
        ('CAMPO', 'Aula de Campo'),
        ('SEMINARIO', 'Seminário'),
        ('WORKSHOP', 'Workshop'),
        ('AVALIACAO', 'Avaliação'),
    ]
    
    STATUS_CHOICES = [
        ('PLANEJADA', 'Planejada'),
        ('REALIZADA', 'Realizada'),
        ('CANCELADA', 'Cancelada'),
        ('ADIADA', 'Adiada'),
    ]
    
    modulo = models.ForeignKey(ModuloPrograma, on_delete=models.CASCADE, related_name='aulas', verbose_name="Módulo")
    numero_aula = models.IntegerField(verbose_name="Número da Aula")
    titulo = models.CharField(max_length=255, verbose_name="Título da Aula")
    tipo_aula = models.CharField(max_length=20, choices=TIPO_AULA_CHOICES, verbose_name="Tipo de Aula")
    
    # Planejamento
    data_planejada = models.DateField(verbose_name="Data Planejada")
    horario_inicio = models.TimeField(verbose_name="Horário de Início")
    horario_fim = models.TimeField(verbose_name="Horário de Término")
    carga_horaria = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Carga Horária")
    
    # Execução
    data_realizada = models.DateField(blank=True, null=True, verbose_name="Data Realizada")
    horario_inicio_real = models.TimeField(blank=True, null=True, verbose_name="Horário Real de Início")
    horario_fim_real = models.TimeField(blank=True, null=True, verbose_name="Horário Real de Término")
    
    # Conteúdo
    objetivos = models.TextField(verbose_name="Objetivos da Aula")
    conteudo = models.TextField(verbose_name="Conteúdo da Aula")
    metodologia = models.TextField(verbose_name="Metodologia Utilizada")
    recursos_utilizados = models.TextField(blank=True, null=True, verbose_name="Recursos Utilizados")
    
    # Professor
    professor = models.ForeignKey(
        Funcionario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='aulas_ministradas',
        verbose_name="Professor"
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANEJADA', verbose_name="Status")
    presentes = models.IntegerField(default=0, verbose_name="Alunos Presentes")
    ausentes = models.IntegerField(default=0, verbose_name="Alunos Ausentes")
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Aula do Programa"
        verbose_name_plural = "Aulas do Programa"
        unique_together = ['modulo', 'numero_aula']
        ordering = ['modulo', 'numero_aula']
    
    def __str__(self):
        return f"{self.modulo.programa.nome} - {self.titulo}"
    
    @property
    def total_alunos(self):
        return self.presentes + self.ausentes
    
    @property
    def taxa_presenca(self):
        total = self.total_alunos
        if total > 0:
            return (self.presentes / total) * 100
        return 0

class FrequenciaPrograma(models.Model):
    participante = models.ForeignKey(ParticipantePrograma, on_delete=models.CASCADE, related_name='frequencias', verbose_name="Participante")
    aula = models.ForeignKey(AulaPrograma, on_delete=models.CASCADE, related_name='frequencias', verbose_name="Aula")
    presente = models.BooleanField(default=True, verbose_name="Presente")
    justificativa_falta = models.TextField(blank=True, null=True, verbose_name="Justificativa da Falta")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Frequência"
        verbose_name_plural = "Frequências"
        unique_together = ['participante', 'aula']
        ordering = ['aula', 'participante']
    
    def __str__(self):
        status = "Presente" if self.presente else "Ausente"
        return f"{self.participante.aluno.nome} - {self.aula.titulo} ({status})"

class AvaliacaoPrograma(models.Model):
    TIPO_AVALIACAO_CHOICES = [
        ('DIAGNOSTICA', 'Diagnóstica'),
        ('FORMATIVA', 'Formativa'),
        ('SOMATIVA', 'Somativa'),
        ('FINAL', 'Final'),
        ('RECUPERACAO', 'Recuperação'),
    ]
    
    modulo = models.ForeignKey(ModuloPrograma, on_delete=models.CASCADE, related_name='avaliacoes', verbose_name="Módulo")
    nome = models.CharField(max_length=255, verbose_name="Nome da Avaliação")
    tipo_avaliacao = models.CharField(max_length=20, choices=TIPO_AVALIACAO_CHOICES, verbose_name="Tipo de Avaliação")
    descricao = models.TextField(verbose_name="Descrição da Avaliação")
    
    # Datas
    data_aplicacao = models.DateField(verbose_name="Data de Aplicação")
    data_limite_entrega = models.DateField(blank=True, null=True, verbose_name="Data Limite de Entrega")
    
    # Configurações
    nota_maxima = models.DecimalField(max_digits=4, decimal_places=2, default=10.0, verbose_name="Nota Máxima")
    peso = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, verbose_name="Peso da Avaliação")
    
    # Professor
    professor_elaborador = models.ForeignKey(
        Funcionario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='avaliacoes_elaboradas',
        verbose_name="Professor Elaborador"
    )
    
    # Critérios
    criterios_avaliacao = models.TextField(verbose_name="Critérios de Avaliação")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Avaliação do Programa"
        verbose_name_plural = "Avaliações do Programa"
        ordering = ['modulo', 'data_aplicacao']
    
    def __str__(self):
        return f"{self.modulo.programa.nome} - {self.nome}"

class NotaPrograma(models.Model):
    participante = models.ForeignKey(ParticipantePrograma, on_delete=models.CASCADE, related_name='notas', verbose_name="Participante")
    avaliacao = models.ForeignKey(AvaliacaoPrograma, on_delete=models.CASCADE, related_name='notas', verbose_name="Avaliação")
    nota = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Nota")
    data_aplicacao = models.DateField(verbose_name="Data da Aplicação")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Nota do Programa"
        verbose_name_plural = "Notas do Programa"
        unique_together = ['participante', 'avaliacao']
        ordering = ['avaliacao', 'participante']
    
    def __str__(self):
        return f"{self.participante.aluno.nome} - {self.avaliacao.nome} ({self.nota})"
    
    @property
    def nota_percentual(self):
        return (self.nota / self.avaliacao.nota_maxima) * 100
