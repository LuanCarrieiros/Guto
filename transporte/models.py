from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from alunos.models import Aluno
from funcionarios.models import Funcionario
from datetime import date

class Motorista(models.Model):
    TIPO_CNH_CHOICES = [
        ('A', 'Categoria A - Motocicletas'),
        ('B', 'Categoria B - Automóveis'),
        ('C', 'Categoria C - Caminhões'),
        ('D', 'Categoria D - Ônibus'),
        ('E', 'Categoria E - Carretas'),
    ]
    
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    rg = models.CharField(max_length=20, blank=True, null=True, verbose_name="RG")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    celular = models.CharField(max_length=20, verbose_name="Celular")
    endereco = models.TextField(verbose_name="Endereço")
    
    # Documentação específica
    cnh_numero = models.CharField(max_length=20, verbose_name="Número da CNH")
    cnh_categoria = models.CharField(max_length=2, choices=TIPO_CNH_CHOICES, verbose_name="Categoria da CNH")
    cnh_validade = models.DateField(verbose_name="Validade da CNH")
    
    # Contrato
    data_inicio_contrato = models.DateField(verbose_name="Início do Contrato")
    data_fim_contrato = models.DateField(blank=True, null=True, verbose_name="Fim do Contrato")
    salario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salário")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Motorista"
        verbose_name_plural = "Motoristas"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    @property
    def idade(self):
        today = date.today()
        return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))
    
    @property
    def cnh_vencida(self):
        return self.cnh_validade < date.today()

class Veiculo(models.Model):
    TIPO_VEICULO_CHOICES = [
        ('ONIBUS', 'Ônibus'),
        ('MICRO_ONIBUS', 'Micro-ônibus'),
        ('VAN', 'Van'),
        ('KOMBI', 'Kombi'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('INATIVO', 'Inativo'),
    ]
    
    placa = models.CharField(max_length=8, unique=True, verbose_name="Placa")
    tipo_veiculo = models.CharField(max_length=20, choices=TIPO_VEICULO_CHOICES, verbose_name="Tipo de Veículo")
    marca = models.CharField(max_length=100, verbose_name="Marca")
    modelo = models.CharField(max_length=100, verbose_name="Modelo")
    ano_fabricacao = models.IntegerField(verbose_name="Ano de Fabricação")
    cor = models.CharField(max_length=50, verbose_name="Cor")
    capacidade_passageiros = models.IntegerField(verbose_name="Capacidade de Passageiros")
    
    # Documentação
    renavam = models.CharField(max_length=20, unique=True, verbose_name="RENAVAM")
    chassi = models.CharField(max_length=17, unique=True, verbose_name="Chassi")
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVO', verbose_name="Status")
    km_atual = models.IntegerField(default=0, verbose_name="Quilometragem Atual")
    
    # Vistoria
    data_ultima_vistoria = models.DateField(blank=True, null=True, verbose_name="Última Vistoria")
    proxima_vistoria = models.DateField(blank=True, null=True, verbose_name="Próxima Vistoria")
    
    # Seguro
    seguradora = models.CharField(max_length=100, blank=True, null=True, verbose_name="Seguradora")
    numero_apolice = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número da Apólice")
    validade_seguro = models.DateField(blank=True, null=True, verbose_name="Validade do Seguro")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        ordering = ['placa']
    
    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"
    
    @property
    def vistoria_vencida(self):
        return self.proxima_vistoria and self.proxima_vistoria < date.today()
    
    @property
    def seguro_vencido(self):
        return self.validade_seguro and self.validade_seguro < date.today()

class Rota(models.Model):
    TURNO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
        ('NOTURNO', 'Noturno'),
        ('INTEGRAL', 'Integral'),
    ]
    
    nome = models.CharField(max_length=255, verbose_name="Nome da Rota")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, verbose_name="Turno")
    
    # Horários
    horario_saida_ida = models.TimeField(verbose_name="Horário de Saída (Ida)")
    horario_chegada_ida = models.TimeField(verbose_name="Horário de Chegada (Ida)")
    horario_saida_volta = models.TimeField(verbose_name="Horário de Saída (Volta)")
    horario_chegada_volta = models.TimeField(verbose_name="Horário de Chegada (Volta)")
    
    # Associações
    veiculo = models.ForeignKey(Veiculo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Veículo")
    motorista = models.ForeignKey(Motorista, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Motorista")
    
    # Status
    ativa = models.BooleanField(default=True, verbose_name="Rota Ativa")
    km_total = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="KM Total da Rota")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Rota"
        verbose_name_plural = "Rotas"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.get_turno_display()}"
    
    @property
    def tempo_percurso_ida(self):
        from datetime import datetime, timedelta
        dt_saida = datetime.combine(date.today(), self.horario_saida_ida)
        dt_chegada = datetime.combine(date.today(), self.horario_chegada_ida)
        if dt_chegada < dt_saida:
            dt_chegada += timedelta(days=1)
        return dt_chegada - dt_saida
    
    @property
    def total_alunos(self):
        return self.alunos_rota.filter(ativo=True).count()

class PontoParada(models.Model):
    rota = models.ForeignKey(Rota, on_delete=models.CASCADE, related_name='pontos', verbose_name="Rota")
    nome = models.CharField(max_length=255, verbose_name="Nome do Ponto")
    endereco = models.TextField(verbose_name="Endereço")
    referencia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ponto de Referência")
    
    # Coordenadas (opcional)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, verbose_name="Longitude")
    
    # Horários específicos do ponto
    horario_ida = models.TimeField(verbose_name="Horário da Ida")
    horario_volta = models.TimeField(verbose_name="Horário da Volta")
    
    ordem = models.IntegerField(default=1, verbose_name="Ordem na Rota")
    ativo = models.BooleanField(default=True, verbose_name="Ponto Ativo")
    
    class Meta:
        verbose_name = "Ponto de Parada"
        verbose_name_plural = "Pontos de Parada"
        ordering = ['rota', 'ordem']
        unique_together = ['rota', 'ordem']
    
    def __str__(self):
        return f"{self.nome} - {self.rota.nome}"

class AlunoTransporte(models.Model):
    SITUACAO_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('SUSPENSO', 'Suspenso'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='transporte_info', verbose_name="Aluno")
    rota = models.ForeignKey(Rota, on_delete=models.CASCADE, related_name='alunos_rota', verbose_name="Rota")
    ponto_embarque = models.ForeignKey(PontoParada, on_delete=models.CASCADE, related_name='alunos_embarque', verbose_name="Ponto de Embarque")
    ponto_desembarque = models.ForeignKey(PontoParada, on_delete=models.CASCADE, related_name='alunos_desembarque', verbose_name="Ponto de Desembarque")
    
    # Dados do responsável pelo transporte
    responsavel_nome = models.CharField(max_length=255, verbose_name="Nome do Responsável")
    responsavel_telefone = models.CharField(max_length=20, verbose_name="Telefone do Responsável")
    responsavel_endereco = models.TextField(verbose_name="Endereço do Responsável")
    
    # Controle
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(blank=True, null=True, verbose_name="Data de Fim")
    situacao = models.CharField(max_length=20, choices=SITUACAO_CHOICES, default='ATIVO', verbose_name="Situação")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Aluno no Transporte"
        verbose_name_plural = "Alunos no Transporte"
        unique_together = ['aluno', 'rota']
        ordering = ['aluno__nome']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.rota.nome}"

class RegistroViagem(models.Model):
    TIPO_VIAGEM_CHOICES = [
        ('IDA', 'Ida'),
        ('VOLTA', 'Volta'),
    ]
    
    rota = models.ForeignKey(Rota, on_delete=models.CASCADE, related_name='viagens', verbose_name="Rota")
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE, verbose_name="Motorista")
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, verbose_name="Veículo")
    
    data_viagem = models.DateField(verbose_name="Data da Viagem")
    tipo_viagem = models.CharField(max_length=10, choices=TIPO_VIAGEM_CHOICES, verbose_name="Tipo de Viagem")
    
    # Horários reais
    horario_saida_real = models.TimeField(blank=True, null=True, verbose_name="Horário Real de Saída")
    horario_chegada_real = models.TimeField(blank=True, null=True, verbose_name="Horário Real de Chegada")
    
    # Controle
    km_inicial = models.IntegerField(verbose_name="KM Inicial")
    km_final = models.IntegerField(blank=True, null=True, verbose_name="KM Final")
    alunos_transportados = models.IntegerField(default=0, verbose_name="Alunos Transportados")
    
    # Status
    concluida = models.BooleanField(default=False, verbose_name="Viagem Concluída")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Registro de Viagem"
        verbose_name_plural = "Registros de Viagem"
        unique_together = ['rota', 'data_viagem', 'tipo_viagem']
        ordering = ['-data_viagem', 'tipo_viagem']
    
    def __str__(self):
        return f"{self.rota.nome} - {self.data_viagem} ({self.get_tipo_viagem_display()})"
    
    @property
    def km_percorridos(self):
        if self.km_final:
            return self.km_final - self.km_inicial
        return 0

class ManutencaoVeiculo(models.Model):
    TIPO_MANUTENCAO_CHOICES = [
        ('PREVENTIVA', 'Preventiva'),
        ('CORRETIVA', 'Corretiva'),
        ('REVISAO', 'Revisão'),
        ('VISTORIA', 'Vistoria'),
    ]
    
    STATUS_CHOICES = [
        ('AGENDADA', 'Agendada'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name='manutencoes', verbose_name="Veículo")
    tipo_manutencao = models.CharField(max_length=20, choices=TIPO_MANUTENCAO_CHOICES, verbose_name="Tipo de Manutenção")
    descricao = models.TextField(verbose_name="Descrição do Serviço")
    
    # Datas
    data_agendamento = models.DateField(verbose_name="Data do Agendamento")
    data_inicio = models.DateField(blank=True, null=True, verbose_name="Data de Início")
    data_conclusao = models.DateField(blank=True, null=True, verbose_name="Data de Conclusão")
    
    # Prestador de serviço
    oficina_prestador = models.CharField(max_length=255, verbose_name="Oficina/Prestador")
    telefone_prestador = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone do Prestador")
    
    # Custos
    valor_orcamento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Valor do Orçamento")
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Valor Final")
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADA', verbose_name="Status")
    km_veiculo = models.IntegerField(verbose_name="KM do Veículo")
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário que Cadastrou")
    
    class Meta:
        verbose_name = "Manutenção de Veículo"
        verbose_name_plural = "Manutenções de Veículos"
        ordering = ['-data_agendamento']
    
    def __str__(self):
        return f"{self.veiculo.placa} - {self.get_tipo_manutencao_display()} ({self.data_agendamento})"
