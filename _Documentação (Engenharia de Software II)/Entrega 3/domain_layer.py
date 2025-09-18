"""
SISTEMA GUTO - CAMADA DE DOMÍNIO
Implementação das Classes Principais de Domínio
Entrega 3 - Engenharia de Software II

Este módulo implementa as classes de domínio puras, sem dependências
de frameworks, focando nos conceitos de Orientação a Objetos.
"""

from datetime import date, datetime
from typing import List, Optional
from enum import Enum


# ================================================================
# ENUMERAÇÕES DE DOMÍNIO
# ================================================================

class TipoEnsino(Enum):
    """Tipos de ensino oferecidos pela escola"""
    EDUCACAO_INFANTIL = "Educação Infantil"
    ENSINO_FUNDAMENTAL_I = "Ensino Fundamental I"
    ENSINO_FUNDAMENTAL_II = "Ensino Fundamental II"
    ENSINO_MEDIO = "Ensino Médio"


class Turno(Enum):
    """Turnos de funcionamento da escola"""
    MATUTINO = "Matutino"
    VESPERTINO = "Vespertino"
    NOTURNO = "Noturno"
    INTEGRAL = "Integral"


class StatusFuncionario(Enum):
    """Status do funcionário na escola"""
    ATIVO = "Ativo"
    INATIVO = "Inativo"
    LICENCA = "Licença"


class TipoMatricula(Enum):
    """Tipos de matrícula de alunos"""
    NOVA = "Nova"
    RENOVACAO = "Renovação"
    TRANSFERENCIA = "Transferência"


# ================================================================
# CLASSE BASE - PESSOA
# Demonstra HERANÇA e ENCAPSULAMENTO
# ================================================================

class Pessoa:
    """
    Classe base para Pessoa
    Demonstra: Encapsulamento, Herança, Abstração
    """

    def __init__(self, nome: str, data_nascimento: date, cpf: str = None):
        # Atributos privados (encapsulamento)
        self.__nome = self._validar_nome(nome)
        self.__data_nascimento = self._validar_data_nascimento(data_nascimento)
        self.__cpf = cpf
        self._data_cadastro = datetime.now()

    # Propriedades (getters/setters) - Encapsulamento
    @property
    def nome(self) -> str:
        """Getter para nome"""
        return self.__nome

    @nome.setter
    def nome(self, valor: str):
        """Setter para nome com validação"""
        self.__nome = self._validar_nome(valor)

    @property
    def data_nascimento(self) -> date:
        """Getter para data de nascimento"""
        return self.__data_nascimento

    @property
    def cpf(self) -> str:
        """Getter para CPF"""
        return self.__cpf

    @cpf.setter
    def cpf(self, valor: str):
        """Setter para CPF com validação"""
        if valor and not self._validar_cpf(valor):
            raise ValueError("CPF inválido")
        self.__cpf = valor

    @property
    def idade(self) -> int:
        """Propriedade calculada - idade atual"""
        hoje = date.today()
        return hoje.year - self.__data_nascimento.year - (
            (hoje.month, hoje.day) <
            (self.__data_nascimento.month, self.__data_nascimento.day)
        )

    # Métodos protegidos (validação) - Encapsulamento
    def _validar_nome(self, nome: str) -> str:
        """Valida nome da pessoa"""
        if not nome or len(nome.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        return nome.strip().title()

    def _validar_data_nascimento(self, data: date) -> date:
        """Valida data de nascimento"""
        if data > date.today():
            raise ValueError("Data de nascimento não pode ser futura")
        return data

    def _validar_cpf(self, cpf: str) -> bool:
        """Validação simples de CPF"""
        cpf_numeros = ''.join(filter(str.isdigit, cpf))
        return len(cpf_numeros) == 11

    # Método público - Polimorfismo
    def obter_informacoes_basicas(self) -> dict:
        """Retorna informações básicas da pessoa"""
        return {
            'nome': self.__nome,
            'idade': self.idade,
            'data_nascimento': self.__data_nascimento.isoformat()
        }

    def __str__(self) -> str:
        """Representação string da pessoa"""
        return f"{self.__nome} ({self.idade} anos)"


# ================================================================
# CLASSE ALUNO - HERDA DE PESSOA
# Demonstra HERANÇA, COMPOSIÇÃO, AGREGAÇÃO
# ================================================================

class Aluno(Pessoa):
    """
    Classe Aluno - representa um estudante
    Demonstra: Herança, Composição, Encapsulamento, Polimorfismo
    """

    def __init__(self, nome: str, data_nascimento: date, sexo: str,
                 nome_mae: str = None, nome_pai: str = None):
        # Chama construtor da classe pai (herança)
        super().__init__(nome, data_nascimento)

        # Atributos específicos do aluno
        self.__codigo = None  # Será definido ao cadastrar
        self.__sexo = self._validar_sexo(sexo)
        self.__nome_mae = nome_mae
        self.__nome_pai = nome_pai
        self.__tipo_arquivo = "ativo"

        # Composição - listas próprias do aluno
        self.__matriculas: List['Matricula'] = []
        self.__responsaveis: List['Responsavel'] = []

        # Agregação - pode existir sem transporte
        self.__transporte: Optional['TransporteAluno'] = None

    # Propriedades específicas do aluno
    @property
    def codigo(self) -> Optional[int]:
        """Código único do aluno"""
        return self.__codigo

    @property
    def sexo(self) -> str:
        """Sexo do aluno"""
        return self.__sexo

    @property
    def nome_mae(self) -> Optional[str]:
        """Nome da mãe"""
        return self.__nome_mae

    @property
    def nome_pai(self) -> Optional[str]:
        """Nome do pai"""
        return self.__nome_pai

    @property
    def matriculas(self) -> List['Matricula']:
        """Lista de matrículas do aluno (composição)"""
        return self.__matriculas.copy()  # Retorna cópia para proteção

    @property
    def responsaveis(self) -> List['Responsavel']:
        """Lista de responsáveis (composição)"""
        return self.__responsaveis.copy()

    # Métodos de negócio específicos do domínio educacional
    def definir_codigo(self, codigo: int):
        """Define código do aluno (só pode ser feito uma vez)"""
        if self.__codigo is not None:
            raise ValueError("Código do aluno já foi definido")
        if codigo <= 0:
            raise ValueError("Código deve ser positivo")
        self.__codigo = codigo

    def adicionar_responsavel(self, responsavel: 'Responsavel'):
        """Adiciona responsável ao aluno (composição)"""
        if not isinstance(responsavel, Responsavel):
            raise TypeError("Deve ser uma instância de Responsavel")
        self.__responsaveis.append(responsavel)

    def remover_responsavel(self, responsavel: 'Responsavel'):
        """Remove responsável do aluno"""
        if responsavel in self.__responsaveis:
            self.__responsaveis.remove(responsavel)

    def adicionar_matricula(self, matricula: 'Matricula'):
        """Adiciona matrícula ao aluno (composição)"""
        if not isinstance(matricula, Matricula):
            raise TypeError("Deve ser uma instância de Matricula")

        # Regra de negócio: só uma matrícula ativa por período
        for mat in self.__matriculas:
            if (mat.ano_administrativo == matricula.ano_administrativo and
                mat.status == "ativa"):
                raise ValueError("Aluno já possui matrícula ativa neste período")

        self.__matriculas.append(matricula)

    def definir_transporte(self, transporte: 'TransporteAluno'):
        """Define transporte do aluno (agregação)"""
        self.__transporte = transporte

    def tem_matricula_ativa(self) -> bool:
        """Verifica se aluno tem matrícula ativa"""
        return any(mat.status == "ativa" for mat in self.__matriculas)

    def obter_matricula_atual(self) -> Optional['Matricula']:
        """Retorna matrícula ativa atual"""
        matriculas_ativas = [m for m in self.__matriculas if m.status == "ativa"]
        return matriculas_ativas[0] if matriculas_ativas else None

    def arquivar(self):
        """Arquiva aluno (soft delete)"""
        self.__tipo_arquivo = "permanente"

    def _validar_sexo(self, sexo: str) -> str:
        """Valida sexo do aluno"""
        sexo_upper = sexo.upper()
        if sexo_upper not in ['M', 'F']:
            raise ValueError("Sexo deve ser 'M' ou 'F'")
        return sexo_upper

    # Polimorfismo - sobrescreve método da classe pai
    def obter_informacoes_basicas(self) -> dict:
        """Sobrescreve método da classe pai (polimorfismo)"""
        info = super().obter_informacoes_basicas()
        info.update({
            'codigo': self.__codigo,
            'sexo': self.__sexo,
            'matriculas_ativas': len([m for m in self.__matriculas if m.status == "ativa"]),
            'responsaveis': len(self.__responsaveis)
        })
        return info

    def __str__(self) -> str:
        """Representação string do aluno"""
        return f"Aluno {self.__codigo}: {self.nome} ({self.idade} anos)"


# ================================================================
# CLASSE FUNCIONARIO - HERDA DE PESSOA
# Demonstra HERANÇA, ENCAPSULAMENTO
# ================================================================

class Funcionario(Pessoa):
    """
    Classe Funcionario - representa um funcionário da escola
    Demonstra: Herança, Encapsulamento, Métodos de Negócio
    """

    def __init__(self, nome: str, data_nascimento: date, cpf: str, cargo: str,
                 telefone: str = None, email: str = None):
        # Chama construtor da classe pai
        super().__init__(nome, data_nascimento, cpf)

        # Atributos específicos do funcionário
        self.__codigo = None
        self.__cargo = self._validar_cargo(cargo)
        self.__telefone = telefone
        self.__email = self._validar_email(email) if email else None
        self.__data_admissao = None
        self.__status = StatusFuncionario.ATIVO

    # Propriedades do funcionário
    @property
    def codigo(self) -> Optional[int]:
        """Código do funcionário"""
        return self.__codigo

    @property
    def cargo(self) -> str:
        """Cargo do funcionário"""
        return self.__cargo

    @cargo.setter
    def cargo(self, valor: str):
        """Setter para cargo com validação"""
        self.__cargo = self._validar_cargo(valor)

    @property
    def telefone(self) -> Optional[str]:
        """Telefone do funcionário"""
        return self.__telefone

    @telefone.setter
    def telefone(self, valor: str):
        """Setter para telefone"""
        self.__telefone = valor

    @property
    def email(self) -> Optional[str]:
        """Email do funcionário"""
        return self.__email

    @email.setter
    def email(self, valor: str):
        """Setter para email com validação"""
        self.__email = self._validar_email(valor) if valor else None

    @property
    def data_admissao(self) -> Optional[date]:
        """Data de admissão"""
        return self.__data_admissao

    @property
    def status(self) -> StatusFuncionario:
        """Status do funcionário"""
        return self.__status

    # Métodos de negócio
    def definir_codigo(self, codigo: int):
        """Define código do funcionário"""
        if self.__codigo is not None:
            raise ValueError("Código já foi definido")
        if codigo <= 0:
            raise ValueError("Código deve ser positivo")
        self.__codigo = codigo

    def admitir(self, data_admissao: date = None):
        """Admite funcionário"""
        self.__data_admissao = data_admissao or date.today()
        self.__status = StatusFuncionario.ATIVO

    def inativar(self):
        """Inativa funcionário"""
        self.__status = StatusFuncionario.INATIVO

    def colocar_em_licenca(self):
        """Coloca funcionário em licença"""
        self.__status = StatusFuncionario.LICENCA

    def esta_ativo(self) -> bool:
        """Verifica se funcionário está ativo"""
        return self.__status == StatusFuncionario.ATIVO

    def obter_tempo_servico(self) -> Optional[int]:
        """Calcula tempo de serviço em dias"""
        if not self.__data_admissao:
            return None
        return (date.today() - self.__data_admissao).days

    # Métodos de validação
    def _validar_cargo(self, cargo: str) -> str:
        """Valida cargo do funcionário"""
        if not cargo or len(cargo.strip()) < 3:
            raise ValueError("Cargo deve ter pelo menos 3 caracteres")
        return cargo.strip().title()

    def _validar_email(self, email: str) -> str:
        """Validação simples de email"""
        if email and '@' not in email:
            raise ValueError("Email inválido")
        return email.lower() if email else None

    # Polimorfismo
    def obter_informacoes_basicas(self) -> dict:
        """Sobrescreve método da classe pai"""
        info = super().obter_informacoes_basicas()
        info.update({
            'codigo': self.__codigo,
            'cargo': self.__cargo,
            'status': self.__status.value,
            'tempo_servico_dias': self.obter_tempo_servico()
        })
        return info

    def __str__(self) -> str:
        """Representação string do funcionário"""
        return f"Funcionário {self.__codigo}: {self.nome} - {self.__cargo}"


# ================================================================
# CLASSE TURMA - ENTIDADE INDEPENDENTE
# Demonstra COMPOSIÇÃO, AGREGAÇÃO, MÉTODOS DE NEGÓCIO
# ================================================================

class Turma:
    """
    Classe Turma - representa uma turma escolar
    Demonstra: Composição, Agregação, Encapsulamento, Métodos de Negócio
    """

    def __init__(self, nome: str, periodo_letivo: str, tipo_ensino: TipoEnsino,
                 ano_serie: str, turno: Turno, vagas_total: int = 30):
        # Atributos básicos da turma
        self.__id = None
        self.__nome = self._validar_nome(nome)
        self.__periodo_letivo = self._validar_periodo(periodo_letivo)
        self.__tipo_ensino = tipo_ensino
        self.__ano_serie = ano_serie
        self.__turno = turno
        self.__vagas_total = self._validar_vagas(vagas_total)
        self.__diario_fechado = False
        self.__data_criacao = datetime.now()

        # Composição - alunos matriculados na turma
        self.__alunos_matriculados: List[Aluno] = []

        # Agregação - professor pode existir independente da turma
        self.__professor_regente: Optional[Funcionario] = None

    # Propriedades da turma
    @property
    def id(self) -> Optional[int]:
        """ID da turma"""
        return self.__id

    @property
    def nome(self) -> str:
        """Nome da turma"""
        return self.__nome

    @property
    def periodo_letivo(self) -> str:
        """Período letivo"""
        return self.__periodo_letivo

    @property
    def tipo_ensino(self) -> TipoEnsino:
        """Tipo de ensino"""
        return self.__tipo_ensino

    @property
    def ano_serie(self) -> str:
        """Ano/série da turma"""
        return self.__ano_serie

    @property
    def turno(self) -> Turno:
        """Turno da turma"""
        return self.__turno

    @property
    def vagas_total(self) -> int:
        """Total de vagas"""
        return self.__vagas_total

    @property
    def vagas_ocupadas(self) -> int:
        """Vagas ocupadas (alunos matriculados)"""
        return len(self.__alunos_matriculados)

    @property
    def vagas_disponiveis(self) -> int:
        """Vagas disponíveis"""
        return self.__vagas_total - self.vagas_ocupadas

    @property
    def diario_fechado(self) -> bool:
        """Status do diário"""
        return self.__diario_fechado

    @property
    def professor_regente(self) -> Optional[Funcionario]:
        """Professor regente da turma"""
        return self.__professor_regente

    @property
    def alunos_matriculados(self) -> List[Aluno]:
        """Lista de alunos matriculados"""
        return self.__alunos_matriculados.copy()

    # Métodos de negócio da turma
    def definir_id(self, id_turma: int):
        """Define ID da turma"""
        if self.__id is not None:
            raise ValueError("ID já foi definido")
        if id_turma <= 0:
            raise ValueError("ID deve ser positivo")
        self.__id = id_turma

    def definir_professor_regente(self, professor: Funcionario):
        """Define professor regente (agregação)"""
        if not isinstance(professor, Funcionario):
            raise TypeError("Deve ser uma instância de Funcionario")
        if not professor.esta_ativo():
            raise ValueError("Professor deve estar ativo")
        self.__professor_regente = professor

    def matricular_aluno(self, aluno: Aluno):
        """Matricula aluno na turma (composição)"""
        if not isinstance(aluno, Aluno):
            raise TypeError("Deve ser uma instância de Aluno")

        if aluno in self.__alunos_matriculados:
            raise ValueError("Aluno já está matriculado nesta turma")

        if self.vagas_disponiveis <= 0:
            raise ValueError("Turma não possui vagas disponíveis")

        self.__alunos_matriculados.append(aluno)

    def desmatricular_aluno(self, aluno: Aluno):
        """Desmatricula aluno da turma"""
        if aluno in self.__alunos_matriculados:
            self.__alunos_matriculados.remove(aluno)
        else:
            raise ValueError("Aluno não está matriculado nesta turma")

    def fechar_diario(self):
        """Fecha diário da turma"""
        if self.__diario_fechado:
            raise ValueError("Diário já está fechado")
        self.__diario_fechado = True

    def reabrir_diario(self):
        """Reabre diário da turma"""
        if not self.__diario_fechado:
            raise ValueError("Diário não está fechado")
        self.__diario_fechado = False

    def esta_lotada(self) -> bool:
        """Verifica se turma está lotada"""
        return self.vagas_disponiveis == 0

    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas da turma"""
        return {
            'nome': self.__nome,
            'periodo_letivo': self.__periodo_letivo,
            'tipo_ensino': self.__tipo_ensino.value,
            'ano_serie': self.__ano_serie,
            'turno': self.__turno.value,
            'vagas_total': self.__vagas_total,
            'vagas_ocupadas': self.vagas_ocupadas,
            'vagas_disponiveis': self.vagas_disponiveis,
            'percentual_ocupacao': round((self.vagas_ocupadas / self.__vagas_total) * 100, 2),
            'diario_fechado': self.__diario_fechado,
            'tem_professor': self.__professor_regente is not None
        }

    # Métodos de validação
    def _validar_nome(self, nome: str) -> str:
        """Valida nome da turma"""
        if not nome or len(nome.strip()) < 2:
            raise ValueError("Nome da turma deve ter pelo menos 2 caracteres")
        return nome.strip()

    def _validar_periodo(self, periodo: str) -> str:
        """Valida período letivo"""
        if not periodo or len(periodo) != 4 or not periodo.isdigit():
            raise ValueError("Período letivo deve ser um ano de 4 dígitos")
        ano = int(periodo)
        if ano < 2020 or ano > 2030:
            raise ValueError("Período letivo deve estar entre 2020 e 2030")
        return periodo

    def _validar_vagas(self, vagas: int) -> int:
        """Valida número de vagas"""
        if vagas <= 0 or vagas > 50:
            raise ValueError("Número de vagas deve estar entre 1 e 50")
        return vagas

    def __str__(self) -> str:
        """Representação string da turma"""
        return f"Turma {self.__id}: {self.__nome} - {self.__ano_serie} ({self.__turno.value})"


# ================================================================
# CLASSES DE APOIO - COMPOSIÇÃO E AGREGAÇÃO
# ================================================================

class Responsavel:
    """
    Classe Responsavel - responsável pelo aluno
    Demonstra: Composição (faz parte do aluno)
    """

    def __init__(self, nome: str, parentesco: str, telefone: str = None, email: str = None):
        self.__nome = self._validar_nome(nome)
        self.__parentesco = parentesco
        self.__telefone = telefone
        self.__email = email

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def parentesco(self) -> str:
        return self.__parentesco

    @property
    def telefone(self) -> Optional[str]:
        return self.__telefone

    @property
    def email(self) -> Optional[str]:
        return self.__email

    def _validar_nome(self, nome: str) -> str:
        if not nome or len(nome.strip()) < 2:
            raise ValueError("Nome do responsável deve ter pelo menos 2 caracteres")
        return nome.strip().title()

    def __str__(self) -> str:
        return f"{self.__nome} ({self.__parentesco})"


class TransporteAluno:
    """
    Classe TransporteAluno - informações de transporte
    Demonstra: Agregação (pode existir independente do aluno)
    """

    def __init__(self, utiliza_transporte: bool = False, nome_motorista: str = None,
                 placa_veiculo: str = None, rota: str = None):
        self.__utiliza_transporte = utiliza_transporte
        self.__nome_motorista = nome_motorista
        self.__placa_veiculo = placa_veiculo
        self.__rota = rota

    @property
    def utiliza_transporte(self) -> bool:
        return self.__utiliza_transporte

    @property
    def nome_motorista(self) -> Optional[str]:
        return self.__nome_motorista

    @property
    def placa_veiculo(self) -> Optional[str]:
        return self.__placa_veiculo

    @property
    def rota(self) -> Optional[str]:
        return self.__rota

    def definir_transporte(self, nome_motorista: str, placa_veiculo: str, rota: str):
        """Define informações de transporte"""
        self.__utiliza_transporte = True
        self.__nome_motorista = nome_motorista
        self.__placa_veiculo = placa_veiculo
        self.__rota = rota

    def cancelar_transporte(self):
        """Cancela transporte do aluno"""
        self.__utiliza_transporte = False
        self.__nome_motorista = None
        self.__placa_veiculo = None
        self.__rota = None

    def __str__(self) -> str:
        if self.__utiliza_transporte:
            return f"Transporte: {self.__rota} - {self.__nome_motorista}"
        return "Não utiliza transporte"


class Matricula:
    """
    Classe Matricula - representa uma matrícula do aluno
    Demonstra: Composição (faz parte do aluno)
    """

    def __init__(self, ano_administrativo: int, tipo_ensino: str, serie_ano: str,
                 tipo_matricula: TipoMatricula, turno_preferencial: Turno):
        self.__id = None
        self.__ano_administrativo = ano_administrativo
        self.__tipo_ensino = tipo_ensino
        self.__serie_ano = serie_ano
        self.__tipo_matricula = tipo_matricula
        self.__turno_preferencial = turno_preferencial
        self.__data_matricula = date.today()
        self.__status = "ativa"

    @property
    def id(self) -> Optional[int]:
        return self.__id

    @property
    def ano_administrativo(self) -> int:
        return self.__ano_administrativo

    @property
    def tipo_ensino(self) -> str:
        return self.__tipo_ensino

    @property
    def serie_ano(self) -> str:
        return self.__serie_ano

    @property
    def tipo_matricula(self) -> TipoMatricula:
        return self.__tipo_matricula

    @property
    def turno_preferencial(self) -> Turno:
        return self.__turno_preferencial

    @property
    def data_matricula(self) -> date:
        return self.__data_matricula

    @property
    def status(self) -> str:
        return self.__status

    def definir_id(self, id_matricula: int):
        """Define ID da matrícula"""
        if self.__id is not None:
            raise ValueError("ID já foi definido")
        self.__id = id_matricula

    def encerrar(self, motivo: str = "Conclusão"):
        """Encerra matrícula"""
        self.__status = "encerrada"

    def esta_ativa(self) -> bool:
        """Verifica se matrícula está ativa"""
        return self.__status == "ativa"

    def __str__(self) -> str:
        return f"Matrícula {self.__id}: {self.__serie_ano} - {self.__ano_administrativo}"


# ================================================================
# EXEMPLO DE USO DAS CLASSES DE DOMÍNIO
# ================================================================

def exemplo_uso_dominio():
    """
    Demonstra o uso das classes de domínio
    Mostra todos os conceitos de OOP implementados
    """

    print("=== DEMONSTRAÇÃO DA CAMADA DE DOMÍNIO ===\n")

    # 1. CRIANDO FUNCIONÁRIO (HERANÇA)
    print("1. === CRIANDO FUNCIONÁRIO ===")
    professor = Funcionario(
        nome="ana paula costa",
        data_nascimento=date(1985, 8, 20),
        cpf="123.456.789-01",
        cargo="professora de matematica",
        telefone="(31) 99999-0000",
        email="ana.costa@escola.edu.br"
    )
    professor.definir_codigo(1)
    professor.admitir(date(2024, 2, 1))

    print(f"Funcionário criado: {professor}")
    print(f"Está ativo: {professor.esta_ativo()}")
    print(f"Tempo de serviço: {professor.obter_tempo_servico()} dias")

    # 2. CRIANDO ALUNO (HERANÇA + COMPOSIÇÃO)
    print("\n2. === CRIANDO ALUNO ===")
    aluno = Aluno(
        nome="joão silva santos",
        data_nascimento=date(2010, 5, 15),
        sexo="M",
        nome_mae="Maria Silva",
        nome_pai="Carlos Santos"
    )
    aluno.definir_codigo(1)

    # COMPOSIÇÃO - Adicionando responsável
    responsavel = Responsavel(
        nome="maria silva",
        parentesco="Mãe",
        telefone="(31) 98765-4321",
        email="maria.silva@email.com"
    )
    aluno.adicionar_responsavel(responsavel)

    # AGREGAÇÃO - Adicionando transporte
    transporte = TransporteAluno()
    transporte.definir_transporte("José da Silva", "ABC-1234", "Rota Centro")
    aluno.definir_transporte(transporte)

    print(f"Aluno criado: {aluno}")
    print(f"Responsáveis: {len(aluno.responsaveis)}")

    # 3. CRIANDO TURMA (AGREGAÇÃO + COMPOSIÇÃO)
    print("\n3. === CRIANDO TURMA ===")
    turma = Turma(
        nome="7º Ano A",
        periodo_letivo="2025",
        tipo_ensino=TipoEnsino.ENSINO_FUNDAMENTAL_II,
        ano_serie="7º Ano",
        turno=Turno.MATUTINO,
        vagas_total=35
    )
    turma.definir_id(1)

    # AGREGAÇÃO - Professor regente
    turma.definir_professor_regente(professor)

    # COMPOSIÇÃO - Matriculando aluno
    turma.matricular_aluno(aluno)

    print(f"Turma criada: {turma}")
    print(f"Vagas ocupadas: {turma.vagas_ocupadas}/{turma.vagas_total}")

    # 4. CRIANDO MATRÍCULA (COMPOSIÇÃO)
    print("\n4. === CRIANDO MATRÍCULA ===")
    matricula = Matricula(
        ano_administrativo=2025,
        tipo_ensino="Ensino Fundamental II",
        serie_ano="7º Ano",
        tipo_matricula=TipoMatricula.NOVA,
        turno_preferencial=Turno.MATUTINO
    )
    matricula.definir_id(1)
    aluno.adicionar_matricula(matricula)

    print(f"Matrícula criada: {matricula}")
    print(f"Aluno tem matrícula ativa: {aluno.tem_matricula_ativa()}")

    # 5. DEMONSTRANDO POLIMORFISMO
    print("\n5. === POLIMORFISMO ===")
    pessoas = [aluno, professor]

    for pessoa in pessoas:
        print(f"\nInformações de {type(pessoa).__name__}:")
        info = pessoa.obter_informacoes_basicas()
        for chave, valor in info.items():
            print(f"  {chave}: {valor}")

    # 6. DEMONSTRANDO MÉTODOS DE NEGÓCIO
    print("\n6. === MÉTODOS DE NEGÓCIO ===")

    # Estatísticas da turma
    stats = turma.obter_estatisticas()
    print(f"\nEstatísticas da Turma:")
    for chave, valor in stats.items():
        print(f"  {chave}: {valor}")

    # Verificações de negócio
    print(f"\nVerificações de Negócio:")
    print(f"  Turma está lotada: {turma.esta_lotada()}")
    print(f"  Funcionário está ativo: {professor.esta_ativo()}")
    print(f"  Aluno tem matrícula ativa: {aluno.tem_matricula_ativa()}")

    print("\n=== DEMONSTRAÇÃO CONCLUÍDA ===")
    print("Todos os conceitos de OOP foram demonstrados:")
    print("✓ Encapsulamento (atributos privados/protegidos)")
    print("✓ Herança (Pessoa -> Aluno/Funcionário)")
    print("✓ Polimorfismo (método obter_informacoes_basicas)")
    print("✓ Composição (Responsavel, Matricula)")
    print("✓ Agregação (TransporteAluno, Professor)")
    print("✓ Abstração (interfaces bem definidas)")
    print("✓ Métodos de negócio (regras do domínio educacional)")


if __name__ == "__main__":
    exemplo_uso_dominio()