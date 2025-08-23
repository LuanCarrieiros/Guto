from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from datetime import date, datetime
from alunos.models import Aluno

# ============================================
# MÓDULO GERÊNCIA DE USUÁRIOS (RF1803-RF1807)
# ============================================

class GrupoAcesso(models.Model):
    """Model para Grupos de Acesso/Perfis de usuário (RF1806, RF2102)"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Grupo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Grupo Ativo")
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Criado por")
    
    class Meta:
        verbose_name = "Grupo de Acesso"
        verbose_name_plural = "Grupos de Acesso"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Instituicao(models.Model):
    """Model para Instituições do sistema"""
    TIPO_INSTITUICAO_CHOICES = [
        ('ESCOLA', 'Escola'),
        ('SME', 'Secretaria Municipal de Educação'),
        ('SEE', 'Secretaria Estadual de Educação'),
        ('ORGAO_SUPERIOR', 'Órgão Superior'),
    ]
    
    nome = models.CharField(max_length=255, verbose_name="Nome da Instituição")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código da Instituição")
    tipo_instituicao = models.CharField(max_length=20, choices=TIPO_INSTITUICAO_CHOICES, verbose_name="Tipo")
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name="CNPJ")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    ativo = models.BooleanField(default=True, verbose_name="Instituição Ativa")
    
    # Hierarquia
    instituicao_pai = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Instituição Superior")
    
    class Meta:
        verbose_name = "Instituição"
        verbose_name_plural = "Instituições"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.codigo})"

class PerfilUsuario(models.Model):
    """Model estendido para dados dos usuários (RF1803-RF1807)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    cpf = models.CharField(
        max_length=14, unique=True, 
        validators=[RegexValidator(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', 'CPF deve estar no formato XXX.XXX.XXX-XX')],
        verbose_name="CPF (Login)"
    )
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Data de Nascimento")
    primeiro_acesso = models.BooleanField(default=True, verbose_name="Primeiro Acesso")
    senha_temporaria = models.CharField(max_length=128, blank=True, null=True, verbose_name="Senha Temporária")
    
    # Controle de auditoria
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    ultimo_acesso = models.DateTimeField(blank=True, null=True, verbose_name="Último Acesso")
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, related_name='usuarios_criados', verbose_name="Criado por")
    
    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.cpf})"
    
    def tem_acoes_no_sistema(self):
        """Verifica se o usuário já realizou ações no sistema (RNF1801)"""
        return RegistroAuditoria.objects.filter(usuario=self.user).exists()

class AssociacaoUsuarioInstituicao(models.Model):
    """Model para associar usuários a instituições e grupos (RF1806, RF1807)"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE, verbose_name="Instituição")
    grupo_acesso = models.ForeignKey(GrupoAcesso, on_delete=models.CASCADE, verbose_name="Grupo de Acesso")
    ativo = models.BooleanField(default=True, verbose_name="Associação Ativa")
    
    # Controle
    data_associacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Associação")
    data_inativacao = models.DateTimeField(blank=True, null=True, verbose_name="Data de Inativação")
    usuario_associacao = models.ForeignKey(User, on_delete=models.PROTECT, related_name='associacoes_criadas', verbose_name="Usuário que Associou")
    
    class Meta:
        verbose_name = "Associação Usuário-Instituição"
        verbose_name_plural = "Associações Usuário-Instituição"
        unique_together = ['usuario', 'instituicao', 'grupo_acesso']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.instituicao.nome} ({self.grupo_acesso.nome})"

# ============================================
# MÓDULO CONFIGURAÇÕES E DADOS (RF1901-RF1907)
# ============================================

class ConfiguracaoSistema(models.Model):
    """Model para Configurações Gerais do Sistema (RF1907)"""
    chave = models.CharField(max_length=100, unique=True, verbose_name="Chave da Configuração")
    valor = models.TextField(verbose_name="Valor da Configuração")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    tipo_valor = models.CharField(
        max_length=20,
        choices=[
            ('STRING', 'Texto'),
            ('INTEGER', 'Número Inteiro'),
            ('BOOLEAN', 'Verdadeiro/Falso'),
            ('JSON', 'JSON'),
        ],
        default='STRING',
        verbose_name="Tipo do Valor"
    )
    editavel = models.BooleanField(default=True, verbose_name="Editável")
    
    # Controle
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_atualizacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Último Usuário")
    
    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"
        ordering = ['chave']
    
    def __str__(self):
        return f"{self.chave}: {self.descricao}"

class DadoAdicional(models.Model):
    """Model para Dados Adicionais personalizados (RF1901)"""
    rotulo = models.CharField(max_length=100, verbose_name="Rótulo")
    tipo_campo = models.CharField(
        max_length=20,
        choices=[
            ('TEXTO', 'Campo de Texto'),
            ('TEXTAREA', 'Área de Texto'),
            ('NUMERO', 'Número'),
            ('DATA', 'Data'),
            ('CHECKBOX', 'Checkbox'),
            ('SELECT', 'Lista de Seleção'),
        ],
        default='TEXTO',
        verbose_name="Tipo do Campo"
    )
    obrigatorio = models.BooleanField(default=False, verbose_name="Campo Obrigatório")
    opcoes = models.TextField(
        blank=True, null=True,
        help_text="Para campos SELECT, liste as opções separadas por vírgula",
        verbose_name="Opções (para SELECT)"
    )
    ordem = models.IntegerField(default=0, verbose_name="Ordem de Exibição")
    ativo = models.BooleanField(default=True, verbose_name="Campo Ativo")
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Criado por")
    
    class Meta:
        verbose_name = "Dado Adicional"
        verbose_name_plural = "Dados Adicionais"
        ordering = ['ordem', 'rotulo']
    
    def __str__(self):
        return self.rotulo

class ValorDadoAdicional(models.Model):
    """Model para valores dos campos adicionais dos alunos"""
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='dados_adicionais', verbose_name="Aluno")
    dado_adicional = models.ForeignKey(DadoAdicional, on_delete=models.CASCADE, verbose_name="Campo Adicional")
    valor = models.TextField(verbose_name="Valor")
    
    # Controle
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_atualizacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Atualizou")
    
    class Meta:
        verbose_name = "Valor de Dado Adicional"
        verbose_name_plural = "Valores de Dados Adicionais"
        unique_together = ['aluno', 'dado_adicional']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.dado_adicional.rotulo}: {self.valor}"

class MatriculaRapida(models.Model):
    """Model para configuração de Matrícula Rápida (RF1902)"""
    nome = models.CharField(max_length=100, verbose_name="Nome da Configuração")
    ano_administrativo = models.CharField(max_length=4, default=str(date.today().year), verbose_name="Ano Administrativo")
    tipo_ensino = models.CharField(max_length=50, verbose_name="Tipo de Ensino")
    serie = models.CharField(max_length=50, verbose_name="Série")
    turno = models.CharField(max_length=20, blank=True, null=True, verbose_name="Turno")
    ativo = models.BooleanField(default=True, verbose_name="Configuração Ativa")
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Criado por")
    
    class Meta:
        verbose_name = "Configuração de Matrícula Rápida"
        verbose_name_plural = "Configurações de Matrícula Rápida"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.tipo_ensino} {self.serie}"

class CabecalhoRelatorio(models.Model):
    """Model para Cabeçalho de Relatórios (RF1906)"""
    linha = models.IntegerField(verbose_name="Número da Linha")
    tipo_conteudo = models.CharField(
        max_length=20,
        choices=[
            ('BRASAO', 'Brasão'),
            ('TEXTO_PADRAO', 'Texto Padrão'),
            ('TEXTO_LIVRE', 'Texto Livre'),
            ('VAZIO', 'Linha Vazia'),
        ],
        verbose_name="Tipo de Conteúdo"
    )
    conteudo = models.TextField(blank=True, null=True, verbose_name="Conteúdo")
    alinhamento = models.CharField(
        max_length=10,
        choices=[
            ('ESQUERDA', 'Esquerda'),
            ('CENTRO', 'Centro'),
            ('DIREITA', 'Direita'),
        ],
        default='CENTRO',
        verbose_name="Alinhamento"
    )
    tamanho_fonte = models.IntegerField(default=12, verbose_name="Tamanho da Fonte")
    negrito = models.BooleanField(default=False, verbose_name="Negrito")
    ativo = models.BooleanField(default=True, verbose_name="Linha Ativa")
    
    # Controle
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_atualizacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Atualizou")
    
    class Meta:
        verbose_name = "Linha do Cabeçalho"
        verbose_name_plural = "Linhas do Cabeçalho"
        ordering = ['linha']
        unique_together = ['linha']
    
    def __str__(self):
        return f"Linha {self.linha}: {self.get_tipo_conteudo_display()}"

# ============================================
# MÓDULO AUDITORIA E CONSULTAS (RF2001-RF2003)
# ============================================

class RegistroAuditoria(models.Model):
    """Model para Registro de Auditoria (RF2002)"""
    ACAO_CHOICES = [
        ('CREATE', 'Criação'),
        ('UPDATE', 'Alteração'),
        ('DELETE', 'Exclusão'),
        ('VIEW', 'Consulta'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PRINT', 'Impressão'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    data_acao = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora da Ação")
    acao = models.CharField(max_length=10, choices=ACAO_CHOICES, verbose_name="Ação")
    tela = models.CharField(max_length=100, verbose_name="Tela/Módulo")
    funcionalidade = models.CharField(max_length=100, verbose_name="Funcionalidade")
    descricao = models.TextField(verbose_name="Descrição da Ação")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Endereço IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    dados_alterados = models.JSONField(blank=True, null=True, verbose_name="Dados Alterados")
    
    class Meta:
        verbose_name = "Registro de Auditoria"
        verbose_name_plural = "Registros de Auditoria"
        ordering = ['-data_acao']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.get_acao_display()} - {self.tela} - {self.data_acao.strftime('%d/%m/%Y %H:%M')}"

class SolicitacaoTransferencia(models.Model):
    """Model para Solicitações de Transferência (RF2003)"""
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('ACEITA', 'Aceita'),
        ('REJEITADA', 'Rejeitada'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    escola_origem = models.ForeignKey(Instituicao, on_delete=models.CASCADE, related_name='transferencias_enviadas', verbose_name="Escola de Origem")
    escola_destino = models.ForeignKey(Instituicao, on_delete=models.CASCADE, related_name='transferencias_recebidas', verbose_name="Escola de Destino")
    
    # Dados da solicitação
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Solicitação")
    motivo = models.TextField(verbose_name="Motivo da Transferência")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Processamento
    data_processamento = models.DateTimeField(blank=True, null=True, verbose_name="Data de Processamento")
    usuario_processamento = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Usuário que Processou")
    
    # Controle
    usuario_solicitacao = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transferencias_solicitadas', verbose_name="Usuário que Solicitou")
    
    class Meta:
        verbose_name = "Solicitação de Transferência"
        verbose_name_plural = "Solicitações de Transferência"
        ordering = ['-data_solicitacao']
        unique_together = ['aluno', 'escola_origem', 'escola_destino', 'status']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.escola_origem.nome} → {self.escola_destino.nome} ({self.get_status_display()})"

# ============================================
# MÓDULO PERMISSÕES E BLOQUEIOS (RF2101-RF2103)
# ============================================

class PermissaoGrupo(models.Model):
    """Model para Permissões de Grupos de Acesso (RF2102)"""
    grupo = models.ForeignKey(GrupoAcesso, on_delete=models.CASCADE, related_name='permissoes', verbose_name="Grupo de Acesso")
    modulo = models.CharField(max_length=50, verbose_name="Módulo")
    submenu = models.CharField(max_length=50, blank=True, null=True, verbose_name="Submenu")
    funcionalidade = models.CharField(max_length=50, blank=True, null=True, verbose_name="Funcionalidade")
    
    # Tipos de permissão
    visualizar = models.BooleanField(default=False, verbose_name="Visualizar")
    incluir = models.BooleanField(default=False, verbose_name="Incluir")
    alterar = models.BooleanField(default=False, verbose_name="Alterar")
    excluir = models.BooleanField(default=False, verbose_name="Excluir")
    imprimir = models.BooleanField(default=False, verbose_name="Imprimir")
    
    class Meta:
        verbose_name = "Permissão de Grupo"
        verbose_name_plural = "Permissões de Grupos"
        unique_together = ['grupo', 'modulo', 'submenu', 'funcionalidade']
    
    def __str__(self):
        return f"{self.grupo.nome} - {self.modulo}"

class BloqueioFuncionalidade(models.Model):
    """Model para Bloqueio de Funcionalidades (RF2103)"""
    TIPO_BLOQUEIO_CHOICES = [
        ('DIRETO', 'Bloqueio Direto'),
        ('POR_ANO', 'Por Ano Administrativo'),
        ('POR_TIPO_ENSINO', 'Por Tipo de Ensino'),
    ]
    
    FUNCIONALIDADE_CHOICES = [
        ('INCLUIR', 'Incluir'),
        ('ALTERAR', 'Alterar'),
        ('EXCLUIR', 'Excluir'),
        ('TODOS', 'Todas as Funcionalidades'),
    ]
    
    modulo = models.CharField(max_length=50, verbose_name="Módulo")
    funcionalidade = models.CharField(max_length=20, choices=FUNCIONALIDADE_CHOICES, verbose_name="Funcionalidade")
    tipo_bloqueio = models.CharField(max_length=20, choices=TIPO_BLOQUEIO_CHOICES, verbose_name="Tipo de Bloqueio")
    
    # Filtros opcionais
    ano_administrativo = models.CharField(max_length=4, blank=True, null=True, verbose_name="Ano Administrativo")
    tipo_ensino = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo de Ensino")
    
    # Dados do bloqueio
    ativo = models.BooleanField(default=True, verbose_name="Bloqueio Ativo")
    motivo = models.TextField(verbose_name="Motivo do Bloqueio")
    data_inicio = models.DateTimeField(verbose_name="Data de Início do Bloqueio")
    data_fim = models.DateTimeField(blank=True, null=True, verbose_name="Data de Fim do Bloqueio")
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Criou")
    
    class Meta:
        verbose_name = "Bloqueio de Funcionalidade"
        verbose_name_plural = "Bloqueios de Funcionalidades"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.modulo} - {self.get_funcionalidade_display()} ({self.get_tipo_bloqueio_display()})"

# ============================================
# MÓDULO TIPOS DE AVALIAÇÃO (RF1904)
# ============================================

class TipoAvaliacao(models.Model):
    """Model para Tipos de Avaliação (RF1904)"""
    nome = models.CharField(max_length=100, verbose_name="Nome do Tipo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name="Peso")
    valor_maximo = models.DecimalField(max_digits=5, decimal_places=2, default=10.0, verbose_name="Valor Máximo")
    ativo = models.BooleanField(default=True, verbose_name="Tipo Ativo")
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Criado por")
    
    class Meta:
        verbose_name = "Tipo de Avaliação"
        verbose_name_plural = "Tipos de Avaliação"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} (Peso: {self.peso})"
