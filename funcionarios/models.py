from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date

class Funcionario(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]
    
    TIPO_ARQUIVO_CHOICES = [
        ('CORRENTE', 'Arquivo Corrente'),
        ('PERMANENTE', 'Arquivo Permanente'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('SOLTEIRO', 'Solteiro(a)'),
        ('CASADO', 'Casado(a)'),
        ('DIVORCIADO', 'Divorciado(a)'),
        ('VIUVO', 'Viúvo(a)'),
        ('UNIAO_ESTAVEL', 'União Estável'),
    ]
    
    COR_RACA_CHOICES = [
        ('BRANCA', 'Branca'),
        ('PRETA', 'Preta'),
        ('PARDA', 'Parda'),
        ('AMARELA', 'Amarela'),
        ('INDIGENA', 'Indígena'),
        ('NAO_DECLARADO', 'Não declarado'),
    ]
    
    # Dados Pessoais (RF406.3)
    codigo = models.AutoField(primary_key=True, verbose_name="Código")
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    nome_social = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Social")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo")
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, verbose_name="Estado Civil")
    cor_raca = models.CharField(max_length=20, choices=COR_RACA_CHOICES, verbose_name="Cor/Raça")
    nacionalidade = models.CharField(max_length=100, default="Brasileira", verbose_name="Nacionalidade")
    naturalidade = models.CharField(max_length=100, verbose_name="Naturalidade")
    uf_nascimento = models.CharField(max_length=2, verbose_name="UF de Nascimento")
    
    # Filiação
    nome_mae = models.CharField(max_length=255, verbose_name="Nome da Mãe")
    nome_pai = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Pai")
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    
    # Endereço
    cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")
    endereco = models.CharField(max_length=255, verbose_name="Endereço")
    numero = models.CharField(max_length=10, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    uf = models.CharField(max_length=2, verbose_name="UF")
    
    # Controle de arquivo
    tipo_arquivo = models.CharField(max_length=20, choices=TIPO_ARQUIVO_CHOICES, default='CORRENTE', verbose_name="Tipo de Arquivo")
    
    # Foto (RF406.4)
    foto = models.ImageField(upload_to='funcionarios/fotos/', blank=True, null=True, verbose_name="Foto")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, related_name='funcionarios_cadastrados', verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    @property
    def idade(self):
        today = date.today()
        return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))

class DocumentacaoFuncionario(models.Model):
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE, related_name='documentacao')
    
    # Documentos pessoais
    rg = models.CharField(max_length=20, verbose_name="RG")
    rg_orgao_expedidor = models.CharField(max_length=10, verbose_name="Órgão Expedidor")
    rg_uf = models.CharField(max_length=2, verbose_name="UF do RG")
    rg_data_expedicao = models.DateField(blank=True, null=True, verbose_name="Data de Expedição")
    
    cpf = models.CharField(max_length=14, verbose_name="CPF", unique=True)
    nis_pis_pasep = models.CharField(max_length=20, blank=True, null=True, verbose_name="NIS/PIS/PASEP")
    titulo_eleitor = models.CharField(max_length=20, blank=True, null=True, verbose_name="Título de Eleitor")
    
    # Documentos trabalhistas
    carteira_trabalho = models.CharField(max_length=20, blank=True, null=True, verbose_name="Carteira de Trabalho")
    carteira_trabalho_serie = models.CharField(max_length=10, blank=True, null=True, verbose_name="Série")
    carteira_trabalho_uf = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF da Carteira")
    
    class Meta:
        verbose_name = "Documentação do Funcionário"
        verbose_name_plural = "Documentações dos Funcionários"

class DadosFuncionais(models.Model):
    SITUACAO_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('APOSENTADO', 'Aposentado'),
        ('AFASTADO_LICENCA', 'Afastado/Licença'),
        ('CEDIDO', 'Cedido'),
        ('CONTRATO_TERCEIRIZADO', 'Contrato Terceirizado'),
        ('CONTRATO_TEMPORARIO', 'Contrato Temporário'),
        ('FALECIDO', 'Falecido'),
        ('RESCISAO_CONTRATO', 'Rescisão de Contrato'),
        ('DESLIGADO', 'Desligado'),
    ]
    
    FUNCAO_CHOICES = [
        ('DOCENTE', 'Docente'),
        ('AUXILIAR_EDUCACIONAL', 'Auxiliar/Assistente Educacional'),
        ('PROFISSIONAL_MONITOR', 'Profissional/Monitor de Atividade Complementar'),
        ('TRADUTOR_LIBRAS', 'Tradutor Intérprete de LIBRAS'),
        ('DIRETOR', 'Diretor'),
        ('VICE_DIRETOR', 'Vice-Diretor'),
        ('COORDENADOR_PEDAGOGICO', 'Coordenador Pedagógico'),
        ('ORIENTADOR_EDUCACIONAL', 'Orientador Educacional'),
        ('SUPERVISOR_ESCOLAR', 'Supervisor Escolar'),
        ('SECRETARIO_ESCOLAR', 'Secretário Escolar'),
        ('AUXILIAR_SECRETARIA', 'Auxiliar de Secretaria'),
        ('BIBLIOTECARIO', 'Bibliotecário'),
        ('AUXILIAR_BIBLIOTECA', 'Auxiliar de Biblioteca'),
        ('LABORATORISTA', 'Laboratorista'),
        ('AUXILIAR_SERVICOS_GERAIS', 'Auxiliar de Serviços Gerais'),
        ('VIGIA', 'Vigia'),
        ('PORTEIRO', 'Porteiro'),
        ('COZINHEIRO', 'Cozinheiro(a)'),
        ('AUXILIAR_COZINHA', 'Auxiliar de Cozinha'),
        ('NUTRICIONISTA', 'Nutricionista'),
        ('PSICOLOGO', 'Psicólogo'),
        ('ASSISTENTE_SOCIAL', 'Assistente Social'),
        ('OUTRO', 'Outro'),
    ]
    
    TIPO_VINCULO_CHOICES = [
        ('CONCURSADO_EFETIVO', 'Concursado/Efetivo'),
        ('CONTRATO_TEMPORARIO', 'Contrato Temporário'),
        ('CONTRATO_TERCEIRIZADO', 'Contrato Terceirizado'),
        ('CONTRATO_CLT', 'Contrato CLT'),
        ('COMISSIONADO', 'Comissionado'),
        ('VOLUNTARIO', 'Voluntário'),
    ]
    
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE, related_name='dados_funcionais')
    
    # Campos obrigatórios (RNF404)
    matricula = models.CharField(max_length=20, unique=True, verbose_name="Matrícula")
    funcao = models.CharField(max_length=30, choices=FUNCAO_CHOICES, verbose_name="Função")
    situacao_funcional = models.CharField(max_length=30, choices=SITUACAO_CHOICES, verbose_name="Situação Funcional")
    
    # Dados do vínculo
    tipo_vinculo = models.CharField(max_length=30, choices=TIPO_VINCULO_CHOICES, verbose_name="Tipo de Vínculo")
    data_admissao = models.DateField(verbose_name="Data de Admissão")
    data_demissao = models.DateField(blank=True, null=True, verbose_name="Data de Demissão")
    data_final_contrato = models.DateField(blank=True, null=True, verbose_name="Data Final do Contrato")
    
    # Carga horária
    carga_horaria_semanal = models.IntegerField(default=40, verbose_name="Carga Horária Semanal")
    carga_horaria_contrato = models.IntegerField(default=40, verbose_name="Carga Horária do Contrato")
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Dados Funcionais"
        verbose_name_plural = "Dados Funcionais"

class DuploVinculo(models.Model):
    """RF406.5: Segundo vínculo funcional"""
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='duplos_vinculos')
    
    matricula_secundaria = models.CharField(max_length=20, unique=True, verbose_name="Matrícula Secundária")
    funcao_secundaria = models.CharField(max_length=30, choices=DadosFuncionais.FUNCAO_CHOICES, verbose_name="Função Secundária")
    situacao_secundaria = models.CharField(max_length=30, choices=DadosFuncionais.SITUACAO_CHOICES, verbose_name="Situação Secundária")
    tipo_vinculo_secundario = models.CharField(max_length=30, choices=DadosFuncionais.TIPO_VINCULO_CHOICES, verbose_name="Tipo de Vínculo Secundário")
    
    data_admissao_secundaria = models.DateField(verbose_name="Data de Admissão Secundária")
    data_demissao_secundaria = models.DateField(blank=True, null=True, verbose_name="Data de Demissão Secundária")
    carga_horaria_secundaria = models.IntegerField(default=20, verbose_name="Carga Horária Secundária")
    
    class Meta:
        verbose_name = "Duplo Vínculo"
        verbose_name_plural = "Duplos Vínculos"

class Habilitacao(models.Model):
    TIPO_HABILITACAO_CHOICES = [
        ('LICENCIATURA', 'Licenciatura'),
        ('COMPLEMENTACAO_PEDAGOGICA', 'Complementação Pedagógica'),
        ('FORMACAO_PEDAGOGICA', 'Formação Pedagógica'),
        ('NORMAL_SUPERIOR', 'Normal Superior'),
        ('NORMAL_MEDIO', 'Normal Médio'),
        ('MAGISTEIO', 'Magistério'),
        ('BACHARELADO', 'Bacharelado'),
        ('TECNOLOGO', 'Tecnólogo'),
        ('NAO_TEM', 'Não tem habilitação específica'),
    ]
    
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='habilitacoes')
    tipo_habilitacao = models.CharField(max_length=30, choices=TIPO_HABILITACAO_CHOICES, verbose_name="Tipo de Habilitação")
    area_conhecimento = models.CharField(max_length=255, verbose_name="Área de Conhecimento")
    instituicao = models.CharField(max_length=255, verbose_name="Instituição")
    ano_conclusao = models.IntegerField(verbose_name="Ano de Conclusão")
    
    class Meta:
        verbose_name = "Habilitação"
        verbose_name_plural = "Habilitações"

class Escolaridade(models.Model):
    NIVEL_CHOICES = [
        ('FUNDAMENTAL_INCOMPLETO', 'Ensino Fundamental Incompleto'),
        ('FUNDAMENTAL_COMPLETO', 'Ensino Fundamental Completo'),
        ('MEDIO_INCOMPLETO', 'Ensino Médio Incompleto'),
        ('MEDIO_COMPLETO', 'Ensino Médio Completo'),
        ('SUPERIOR_INCOMPLETO', 'Ensino Superior Incompleto'),
        ('SUPERIOR_COMPLETO', 'Ensino Superior Completo'),
        ('ESPECIALIZACAO', 'Especialização'),
        ('MESTRADO', 'Mestrado'),
        ('DOUTORADO', 'Doutorado'),
        ('POS_DOUTORADO', 'Pós-Doutorado'),
    ]
    
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE, related_name='escolaridade')
    nivel = models.CharField(max_length=30, choices=NIVEL_CHOICES, verbose_name="Nível de Escolaridade")
    curso = models.CharField(max_length=255, blank=True, null=True, verbose_name="Curso")
    instituicao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Instituição")
    ano_conclusao = models.IntegerField(blank=True, null=True, verbose_name="Ano de Conclusão")
    
    class Meta:
        verbose_name = "Escolaridade"
        verbose_name_plural = "Escolaridades"

class FormacaoSuperior(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='formacoes_superiores')
    curso = models.CharField(max_length=255, verbose_name="Curso")
    instituicao = models.CharField(max_length=255, verbose_name="Instituição")
    ano_conclusao = models.IntegerField(verbose_name="Ano de Conclusão")
    tipo_curso = models.CharField(max_length=20, choices=[
        ('GRADUACAO', 'Graduação'),
        ('ESPECIALIZACAO', 'Especialização'),
        ('MESTRADO', 'Mestrado'),
        ('DOUTORADO', 'Doutorado'),
    ], verbose_name="Tipo de Curso")
    
    class Meta:
        verbose_name = "Formação Superior"
        verbose_name_plural = "Formações Superiores"

class Disponibilidade(models.Model):
    TURNO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
        ('NOTURNO', 'Noturno'),
    ]
    
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE, related_name='disponibilidade')
    matutino = models.BooleanField(default=False, verbose_name="Matutino")
    vespertino = models.BooleanField(default=False, verbose_name="Vespertino")
    noturno = models.BooleanField(default=False, verbose_name="Noturno")
    
    class Meta:
        verbose_name = "Disponibilidade"
        verbose_name_plural = "Disponibilidades"

class DisciplinaFuncionario(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='disciplinas')
    disciplina = models.CharField(max_length=255, verbose_name="Disciplina")
    habilitado = models.BooleanField(default=True, verbose_name="Habilitado")
    
    class Meta:
        verbose_name = "Disciplina do Funcionário"
        verbose_name_plural = "Disciplinas dos Funcionários"

class DeficienciaFuncionario(models.Model):
    TIPO_DEFICIENCIA_CHOICES = [
        ('VISUAL', 'Deficiência Visual'),
        ('AUDITIVA', 'Deficiência Auditiva'),
        ('FISICA', 'Deficiência Física'),
        ('INTELECTUAL', 'Deficiência Intelectual'),
        ('MULTIPLA', 'Deficiência Múltipla'),
        ('AUTISM0', 'Transtorno do Espectro Autista'),
        ('OUTRAS', 'Outras'),
    ]
    
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='deficiencias')
    tipo_deficiencia = models.CharField(max_length=20, choices=TIPO_DEFICIENCIA_CHOICES, verbose_name="Tipo de Deficiência")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    class Meta:
        verbose_name = "Deficiência do Funcionário"
        verbose_name_plural = "Deficiências dos Funcionários"

# Models para Associação de Professor (RF501-RF511)
class AssociacaoProfessor(models.Model):
    TIPO_ASSOCIACAO_CHOICES = [
        ('DISCIPLINA', 'Disciplina (frequência individual)'),
        ('TURMA', 'Turma (frequência em grupo)'),
        ('TURMA_AEE', 'Turma AEE/Atividade Complementar'),
    ]
    
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='associacoes')
    turma = models.CharField(max_length=100, verbose_name="Turma")  # Seria FK para model Turma quando implementado
    disciplina = models.CharField(max_length=255, verbose_name="Disciplina")
    tipo_associacao = models.CharField(max_length=20, choices=TIPO_ASSOCIACAO_CHOICES, verbose_name="Tipo de Associação")
    
    # RF506: Histórico com datas
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_termino = models.DateField(blank=True, null=True, verbose_name="Data de Término")
    
    # RF510: Disciplina sem docente
    sem_docente = models.BooleanField(default=False, verbose_name="Disciplina não possui docente")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True)
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, related_name='associacoes_cadastradas')
    
    class Meta:
        verbose_name = "Associação de Professor"
        verbose_name_plural = "Associações de Professores"
        unique_together = ['funcionario', 'turma', 'disciplina', 'data_inicio']

class AssociacaoOutrosProfissionais(models.Model):
    TIPO_PROFISSIONAL_CHOICES = [
        ('AUXILIAR_EDUCACIONAL', 'Auxiliar/Assistente Educacional'),
        ('MONITOR_ATIVIDADE', 'Profissional/Monitor de Atividade Complementar'),
        ('TRADUTOR_LIBRAS', 'Tradutor Intérprete de LIBRAS'),
    ]
    
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='associacoes_outros')
    turma = models.CharField(max_length=100, verbose_name="Turma")
    tipo_profissional = models.CharField(max_length=30, choices=TIPO_PROFISSIONAL_CHOICES, verbose_name="Tipo de Profissional")
    
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_termino = models.DateField(blank=True, null=True, verbose_name="Data de Término")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True)
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, related_name='associacoes_outros_cadastradas')
    
    class Meta:
        verbose_name = "Associação de Outros Profissionais"
        verbose_name_plural = "Associações de Outros Profissionais"
