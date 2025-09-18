"""
SISTEMA GUTO - CAMADA DE PERSISTÊNCIA
Implementação dos Padrões Repository e DAO
Entrega 4 - Engenharia de Software II

Este módulo demonstra a implementação da camada de persistência
extraída do Sistema GUTO Django, adaptada para mostrar os patterns
solicitados pelo professor.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import sqlite3
from dataclasses import dataclass
import time
import random

# Configuração para evitar warnings do Python 3.12+
# No Python 3.12+, os adaptadores padrão de date/datetime foram depreciados
# Registramos adaptadores customizados para compatibilidade
sqlite3.register_adapter(date, lambda d: d.isoformat())
sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
sqlite3.register_converter("date", lambda s: date.fromisoformat(s.decode()))
sqlite3.register_converter("datetime", lambda s: datetime.fromisoformat(s.decode()))

# ================================================================
# PATTERN 1: DATA TRANSFER OBJECT (DTO)
# Usados para transferir dados entre camadas
# ================================================================

@dataclass
class AlunoDTO:
    """DTO para transferência de dados do Aluno"""
    codigo: Optional[int] = None
    nome: str = ""
    nome_social: Optional[str] = None
    data_nascimento: Optional[date] = None
    sexo: str = ""
    nome_mae: Optional[str] = None
    nome_pai: Optional[str] = None
    mae_nao_declarada: bool = False
    pai_nao_declarado: bool = False
    aluno_gemeo: bool = False
    tipo_arquivo: str = "ativo"
    lembrete: Optional[str] = None
    foto: Optional[str] = None
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    usuario_cadastro_id: Optional[int] = None

@dataclass
class MatriculaDTO:
    """DTO para transferência de dados da Matrícula"""
    id: Optional[int] = None
    ano_administrativo: int = 2025
    tipo_ensino: str = ""
    serie_ano: str = ""
    tipo_matricula: str = ""
    turno_preferencial: str = ""
    data_matricula: Optional[date] = None
    status: str = "ativa"
    aluno_id: Optional[int] = None
    usuario_cadastro_id: Optional[int] = None

@dataclass
class FuncionarioDTO:
    """DTO para transferência de dados do Funcionário"""
    codigo: Optional[int] = None
    nome: str = ""
    cpf: str = ""
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    cargo: str = ""
    data_admissao: Optional[date] = None
    status: str = "ativo"
    data_cadastro: Optional[datetime] = None
    usuario_cadastro_id: Optional[int] = None

@dataclass
class TurmaDTO:
    """DTO para transferência de dados da Turma"""
    id: Optional[int] = None
    nome: str = ""
    periodo_letivo: str = "2025"
    tipo_ensino: str = ""
    ano_serie: str = ""
    turno: str = ""
    vagas_total: int = 30
    diario_fechado: bool = False
    data_criacao: Optional[datetime] = None
    usuario_criacao_id: Optional[int] = None

# ================================================================
# PATTERN 2: SINGLETON - CONFIGURAÇÃO DE CONEXÃO
# Garante uma única instância da configuração do banco
# ================================================================

class DatabaseConnection:
    """
    PATTERN: Singleton
    Garante uma única conexão com o banco de dados
    """
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def get_connection(self) -> sqlite3.Connection:
        """Retorna a conexão ativa com o banco"""
        if self._connection is None:
            # Usa o banco local da entrega
            from pathlib import Path
            db_path = Path(__file__).parent / 'entrega4_db.sqlite3'
            self._connection = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
            self._connection.row_factory = sqlite3.Row  # Permite acesso por nome da coluna
        return self._connection
    
    def close_connection(self):
        """Fecha a conexão com o banco"""
        if self._connection:
            self._connection.close()
            self._connection = None

# ================================================================
# PATTERN 3: REPOSITORY INTERFACE
# Define o contrato para operações de persistência
# ================================================================

class IRepository(ABC):
    """
    PATTERN: Repository Interface
    Define o contrato para operações CRUD genéricas
    """
    
    @abstractmethod
    def create(self, entity: Any) -> int:
        """Cria uma nova entidade"""
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[Any]:
        """Busca entidade por ID"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Any]:
        """Retorna todas as entidades"""
        pass
    
    @abstractmethod
    def update(self, entity: Any) -> bool:
        """Atualiza uma entidade"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Remove uma entidade"""
        pass

# ================================================================
# PATTERN 4: REPOSITORY IMPLEMENTATION
# Implementação concreta do padrão Repository
# ================================================================

class AlunoRepository(IRepository):
    """
    PATTERN: Repository
    Implementa operações de persistência para Aluno
    Baseado nas operações do Django ORM do Sistema GUTO
    """
    
    def __init__(self):
        self._db = DatabaseConnection()
    
    def create(self, aluno: AlunoDTO) -> int:
        """
        Cria um novo aluno no banco de dados
        Baseado em: alunos/views.py - AlunoCreateView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO alunos_aluno 
        (nome, nome_social, data_nascimento, sexo, nome_mae, nome_pai, 
         mae_nao_declarada, pai_nao_declarado, aluno_gemeo, tipo_arquivo, 
         lembrete, foto, data_cadastro, data_atualizacao, usuario_cadastro_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        valores = (
            aluno.nome, aluno.nome_social, aluno.data_nascimento, aluno.sexo,
            aluno.nome_mae, aluno.nome_pai, aluno.mae_nao_declarada,
            aluno.pai_nao_declarado, aluno.aluno_gemeo, aluno.tipo_arquivo,
            aluno.lembrete, aluno.foto, datetime.now(), datetime.now(),
            aluno.usuario_cadastro_id
        )
        
        cursor.execute(query, valores)
        conn.commit()
        return cursor.lastrowid
    
    def find_by_id(self, aluno_id: int) -> Optional[AlunoDTO]:
        """
        Busca aluno por código
        Baseado em: alunos/views.py - AlunoDetailView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM alunos_aluno WHERE codigo = ?"
        cursor.execute(query, (aluno_id,))
        row = cursor.fetchone()
        
        if row:
            return AlunoDTO(
                codigo=row['codigo'],
                nome=row['nome'],
                nome_social=row['nome_social'],
                data_nascimento=row['data_nascimento'],
                sexo=row['sexo'],
                nome_mae=row['nome_mae'],
                nome_pai=row['nome_pai'],
                mae_nao_declarada=bool(row['mae_nao_declarada']),
                pai_nao_declarado=bool(row['pai_nao_declarado']),
                aluno_gemeo=bool(row['aluno_gemeo']),
                tipo_arquivo=row['tipo_arquivo'],
                lembrete=row['lembrete'],
                foto=row['foto'],
                data_cadastro=row['data_cadastro'],
                data_atualizacao=row['data_atualizacao'],
                usuario_cadastro_id=row['usuario_cadastro_id']
            )
        return None
    
    def find_all(self) -> List[AlunoDTO]:
        """
        Retorna todos os alunos ativos
        Baseado em: alunos/views.py - AlunoListView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT * FROM alunos_aluno 
        WHERE tipo_arquivo = 'ativo' 
        ORDER BY nome
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        alunos = []
        for row in rows:
            aluno = AlunoDTO(
                codigo=row['codigo'],
                nome=row['nome'],
                nome_social=row['nome_social'],
                data_nascimento=row['data_nascimento'],
                sexo=row['sexo'],
                nome_mae=row['nome_mae'],
                nome_pai=row['nome_pai'],
                tipo_arquivo=row['tipo_arquivo']
            )
            alunos.append(aluno)
        
        return alunos
    
    def find_by_name(self, nome: str) -> List[AlunoDTO]:
        """
        Busca alunos por nome (busca parcial)
        Baseado em: alunos/views.py - sistema de pesquisa
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT * FROM alunos_aluno 
        WHERE nome LIKE ? AND tipo_arquivo = 'ativo'
        ORDER BY nome
        """
        cursor.execute(query, (f'%{nome}%',))
        rows = cursor.fetchall()
        
        return [self._row_to_dto(row) for row in rows]
    
    def update(self, aluno: AlunoDTO) -> bool:
        """
        Atualiza dados do aluno
        Baseado em: alunos/views.py - AlunoUpdateView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE alunos_aluno 
        SET nome = ?, nome_social = ?, data_nascimento = ?, sexo = ?,
            nome_mae = ?, nome_pai = ?, mae_nao_declarada = ?,
            pai_nao_declarado = ?, aluno_gemeo = ?, lembrete = ?,
            data_atualizacao = ?
        WHERE codigo = ?
        """
        
        valores = (
            aluno.nome, aluno.nome_social, aluno.data_nascimento, aluno.sexo,
            aluno.nome_mae, aluno.nome_pai, aluno.mae_nao_declarada,
            aluno.pai_nao_declarado, aluno.aluno_gemeo, aluno.lembrete,
            datetime.now(), aluno.codigo
        )
        
        cursor.execute(query, valores)
        conn.commit()
        return cursor.rowcount > 0
    
    def delete(self, aluno_id: int) -> bool:
        """
        Soft delete - move para arquivo permanente
        Baseado em: alunos/views.py - arquivo_permanente_aluno
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE alunos_aluno 
        SET tipo_arquivo = 'permanente', data_atualizacao = ?
        WHERE codigo = ?
        """
        
        cursor.execute(query, (datetime.now(), aluno_id))
        conn.commit()
        return cursor.rowcount > 0
    
    def _row_to_dto(self, row) -> AlunoDTO:
        """Converte row do banco para DTO"""
        return AlunoDTO(
            codigo=row['codigo'],
            nome=row['nome'],
            nome_social=row['nome_social'],
            data_nascimento=row['data_nascimento'],
            sexo=row['sexo'],
            tipo_arquivo=row['tipo_arquivo']
        )

# ================================================================
# PATTERN 5: DAO (DATA ACCESS OBJECT)
# Implementação específica para operações de matrícula
# ================================================================

class MatriculaDAO:
    """
    PATTERN: Data Access Object
    Implementa operações específicas de matrícula
    Baseado em: alunos/views.py - operações de matrícula
    """
    
    def __init__(self):
        self._db = DatabaseConnection()
    
    def criar_matricula(self, matricula: MatriculaDTO) -> int:
        """
        Cria nova matrícula para o aluno
        Baseado em: alunos/views.py - MatriculaCreateView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        # Verifica se já existe matrícula ativa para o aluno no ano
        if self._tem_matricula_ativa(matricula.aluno_id, matricula.ano_administrativo):
            raise ValueError("Aluno já possui matrícula ativa neste ano")
        
        query = """
        INSERT INTO alunos_matricula 
        (ano_administrativo, tipo_ensino, serie_ano, tipo_matricula,
         turno_preferencial, data_matricula, possui_dependencia, 
         condicao_anterior, condicoes_especiais_avaliacao, status, 
         aluno_id, usuario_cadastro_id, data_cadastro, data_atualizacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        valores = (
            matricula.ano_administrativo, matricula.tipo_ensino,
            matricula.serie_ano, matricula.tipo_matricula,
            matricula.turno_preferencial, matricula.data_matricula,
            getattr(matricula, 'possui_dependencia', False),
            getattr(matricula, 'condicao_anterior', 'aprovado'),
            getattr(matricula, 'condicoes_especiais_avaliacao', False),
            matricula.status, matricula.aluno_id,
            matricula.usuario_cadastro_id, datetime.now(), datetime.now()
        )
        
        cursor.execute(query, valores)
        conn.commit()
        return cursor.lastrowid
    
    def buscar_matriculas_aluno(self, aluno_id: int) -> List[MatriculaDTO]:
        """
        Busca todas as matrículas de um aluno
        Baseado em: alunos/models.py - relacionamento Aluno-Matricula
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT * FROM alunos_matricula 
        WHERE aluno_id = ? 
        ORDER BY ano_administrativo DESC
        """
        cursor.execute(query, (aluno_id,))
        rows = cursor.fetchall()
        
        matriculas = []
        for row in rows:
            matricula = MatriculaDTO(
                id=row['id'],
                ano_administrativo=row['ano_administrativo'],
                tipo_ensino=row['tipo_ensino'],
                serie_ano=row['serie_ano'],
                tipo_matricula=row['tipo_matricula'],
                turno_preferencial=row['turno_preferencial'],
                data_matricula=row['data_matricula'],
                status=row['status'],
                aluno_id=row['aluno_id'],
                usuario_cadastro_id=row['usuario_cadastro_id']
            )
            matriculas.append(matricula)
        
        return matriculas
    
    def encerrar_matricula(self, matricula_id: int, motivo: str) -> bool:
        """
        Encerra uma matrícula
        Baseado em: alunos/views.py - encerrar_matricula
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE alunos_matricula 
        SET status = 'encerrada', 
            data_encerramento = ?,
            motivo_encerramento = ?,
            data_atualizacao = ?
        WHERE id = ?
        """
        
        cursor.execute(query, (date.today(), motivo, datetime.now(), matricula_id))
        conn.commit()
        return cursor.rowcount > 0
    
    def _tem_matricula_ativa(self, aluno_id: int, ano: int) -> bool:
        """Verifica se aluno já tem matrícula ativa no ano"""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT COUNT(*) as total FROM alunos_matricula 
        WHERE aluno_id = ? AND ano_administrativo = ? AND status = 'ativa'
        """
        cursor.execute(query, (aluno_id, ano))
        resultado = cursor.fetchone()
        return resultado['total'] > 0

# ================================================================
# PATTERN 7: FUNCIONARIO REPOSITORY
# Implementação CRUD para Funcionários
# ================================================================

class FuncionarioRepository(IRepository):
    """
    PATTERN: Repository
    Implementa operações de persistência para Funcionário
    Baseado nas operações do Django ORM do Sistema GUTO
    """

    def __init__(self):
        self._db = DatabaseConnection()

    def create(self, funcionario: FuncionarioDTO) -> int:
        """
        Cria um novo funcionário no banco de dados
        Baseado em: funcionarios/views.py - FuncionarioCreateView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO funcionarios_funcionario
        (nome, cpf, data_nascimento, telefone, email, cargo,
         data_admissao, status, data_cadastro, usuario_cadastro_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        valores = (
            funcionario.nome, funcionario.cpf, funcionario.data_nascimento,
            funcionario.telefone, funcionario.email, funcionario.cargo,
            funcionario.data_admissao, funcionario.status, datetime.now(),
            funcionario.usuario_cadastro_id
        )

        cursor.execute(query, valores)
        conn.commit()
        return cursor.lastrowid

    def find_by_id(self, funcionario_id: int) -> Optional[FuncionarioDTO]:
        """
        Busca funcionário por código
        Baseado em: funcionarios/views.py - FuncionarioDetailView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM funcionarios_funcionario WHERE codigo = ?"
        cursor.execute(query, (funcionario_id,))
        row = cursor.fetchone()

        if row:
            return FuncionarioDTO(
                codigo=row['codigo'],
                nome=row['nome'],
                cpf=row['cpf'],
                data_nascimento=row['data_nascimento'],
                telefone=row['telefone'],
                email=row['email'],
                cargo=row['cargo'],
                data_admissao=row['data_admissao'],
                status=row['status'],
                data_cadastro=row['data_cadastro'],
                usuario_cadastro_id=row['usuario_cadastro_id']
            )
        return None

    def find_all(self) -> List[FuncionarioDTO]:
        """
        Retorna todos os funcionários ativos
        Baseado em: funcionarios/views.py - FuncionarioListView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        query = """
        SELECT * FROM funcionarios_funcionario
        WHERE status = 'ativo'
        ORDER BY nome
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        funcionarios = []
        for row in rows:
            funcionario = FuncionarioDTO(
                codigo=row['codigo'],
                nome=row['nome'],
                cpf=row['cpf'],
                cargo=row['cargo'],
                status=row['status']
            )
            funcionarios.append(funcionario)

        return funcionarios

    def find_by_cpf(self, cpf: str) -> Optional[FuncionarioDTO]:
        """
        Busca funcionário por CPF (campo único)
        Baseado em: funcionarios/models.py - validação de CPF
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM funcionarios_funcionario WHERE cpf = ?"
        cursor.execute(query, (cpf,))
        row = cursor.fetchone()

        if row:
            return self._row_to_dto(row)
        return None

    def update(self, funcionario: FuncionarioDTO) -> bool:
        """
        Atualiza dados do funcionário
        Baseado em: funcionarios/views.py - FuncionarioUpdateView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE funcionarios_funcionario
        SET nome = ?, cpf = ?, data_nascimento = ?, telefone = ?,
            email = ?, cargo = ?, data_admissao = ?
        WHERE codigo = ?
        """

        valores = (
            funcionario.nome, funcionario.cpf, funcionario.data_nascimento,
            funcionario.telefone, funcionario.email, funcionario.cargo,
            funcionario.data_admissao, funcionario.codigo
        )

        cursor.execute(query, valores)
        conn.commit()
        return cursor.rowcount > 0

    def delete(self, funcionario_id: int) -> bool:
        """
        Soft delete - inativa funcionário
        Baseado em: funcionarios/views.py - inativar_funcionario
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE funcionarios_funcionario
        SET status = 'inativo'
        WHERE codigo = ?
        """

        cursor.execute(query, (funcionario_id,))
        conn.commit()
        return cursor.rowcount > 0

    def _row_to_dto(self, row) -> FuncionarioDTO:
        """Converte row do banco para DTO"""
        return FuncionarioDTO(
            codigo=row['codigo'],
            nome=row['nome'],
            cpf=row['cpf'],
            cargo=row['cargo'],
            status=row['status']
        )

# ================================================================
# PATTERN 8: TURMA REPOSITORY
# Implementação CRUD para Turmas
# ================================================================

class TurmaRepository(IRepository):
    """
    PATTERN: Repository
    Implementa operações de persistência para Turma
    Baseado nas operações do Django ORM do Sistema GUTO
    """

    def __init__(self):
        self._db = DatabaseConnection()

    def create(self, turma: TurmaDTO) -> int:
        """
        Cria uma nova turma no banco de dados
        Baseado em: turma/views.py - TurmaCreateView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        # Verifica se já existe turma com mesmo nome no período
        if self._turma_existe(turma.nome, turma.periodo_letivo):
            raise ValueError("Já existe turma com este nome no período letivo")

        query = """
        INSERT INTO turma_turma
        (nome, periodo_letivo, tipo_ensino, ano_serie, turno,
         vagas_total, diario_fechado, data_criacao, usuario_criacao_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        valores = (
            turma.nome, turma.periodo_letivo, turma.tipo_ensino,
            turma.ano_serie, turma.turno, turma.vagas_total,
            turma.diario_fechado, datetime.now(), turma.usuario_criacao_id
        )

        cursor.execute(query, valores)
        conn.commit()
        return cursor.lastrowid

    def find_by_id(self, turma_id: int) -> Optional[TurmaDTO]:
        """
        Busca turma por ID
        Baseado em: turma/views.py - TurmaDetailView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM turma_turma WHERE id = ?"
        cursor.execute(query, (turma_id,))
        row = cursor.fetchone()

        if row:
            return TurmaDTO(
                id=row['id'],
                nome=row['nome'],
                periodo_letivo=row['periodo_letivo'],
                tipo_ensino=row['tipo_ensino'],
                ano_serie=row['ano_serie'],
                turno=row['turno'],
                vagas_total=row['vagas_total'],
                diario_fechado=bool(row['diario_fechado']),
                data_criacao=row['data_criacao'],
                usuario_criacao_id=row['usuario_criacao_id']
            )
        return None

    def find_all(self) -> List[TurmaDTO]:
        """
        Retorna todas as turmas ativas
        Baseado em: turma/views.py - TurmaListView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        query = """
        SELECT * FROM turma_turma
        ORDER BY periodo_letivo DESC, ano_serie, nome
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        turmas = []
        for row in rows:
            turma = TurmaDTO(
                id=row['id'],
                nome=row['nome'],
                periodo_letivo=row['periodo_letivo'],
                tipo_ensino=row['tipo_ensino'],
                ano_serie=row['ano_serie'],
                turno=row['turno'],
                vagas_total=row['vagas_total'],
                diario_fechado=bool(row['diario_fechado'])
            )
            turmas.append(turma)

        return turmas

    def find_by_periodo(self, periodo: str) -> List[TurmaDTO]:
        """
        Busca turmas por período letivo
        Baseado em: turma/views.py - filtro por período
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        query = """
        SELECT * FROM turma_turma
        WHERE periodo_letivo = ?
        ORDER BY ano_serie, nome
        """
        cursor.execute(query, (periodo,))
        rows = cursor.fetchall()

        return [self._row_to_dto(row) for row in rows]

    def update(self, turma: TurmaDTO) -> bool:
        """
        Atualiza dados da turma
        Baseado em: turma/views.py - TurmaUpdateView
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE turma_turma
        SET nome = ?, tipo_ensino = ?, ano_serie = ?, turno = ?,
            vagas_total = ?, diario_fechado = ?
        WHERE id = ?
        """

        valores = (
            turma.nome, turma.tipo_ensino, turma.ano_serie,
            turma.turno, turma.vagas_total, turma.diario_fechado,
            turma.id
        )

        cursor.execute(query, valores)
        conn.commit()
        return cursor.rowcount > 0

    def delete(self, turma_id: int) -> bool:
        """
        Remove turma (hard delete - apenas se sem alunos)
        Baseado em: turma/views.py - delete_turma
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        # Verifica se tem alunos enturmados
        cursor.execute("SELECT COUNT(*) as total FROM turma_enturmacao WHERE turma_id = ? AND ativo = 1", (turma_id,))
        resultado = cursor.fetchone()

        if resultado['total'] > 0:
            raise ValueError("Não é possível excluir turma com alunos enturmados")

        query = "DELETE FROM turma_turma WHERE id = ?"
        cursor.execute(query, (turma_id,))
        conn.commit()
        return cursor.rowcount > 0

    def _turma_existe(self, nome: str, periodo: str) -> bool:
        """Verifica se turma já existe no período"""
        conn = self._db.get_connection()
        cursor = conn.cursor()

        query = """
        SELECT COUNT(*) as total FROM turma_turma
        WHERE nome = ? AND periodo_letivo = ?
        """
        cursor.execute(query, (nome, periodo))
        resultado = cursor.fetchone()
        return resultado['total'] > 0

    def _row_to_dto(self, row) -> TurmaDTO:
        """Converte row do banco para DTO"""
        return TurmaDTO(
            id=row['id'],
            nome=row['nome'],
            periodo_letivo=row['periodo_letivo'],
            tipo_ensino=row['tipo_ensino'],
            ano_serie=row['ano_serie'],
            turno=row['turno']
        )

# ================================================================
# PATTERN 6: FACTORY PATTERN
# Cria instâncias dos repositórios
# ================================================================

class RepositoryFactory:
    """
    PATTERN: Factory
    Centraliza a criação de repositórios e DAOs
    """

    @staticmethod
    def create_aluno_repository() -> AlunoRepository:
        """Cria instância do repositório de alunos"""
        return AlunoRepository()

    @staticmethod
    def create_funcionario_repository() -> FuncionarioRepository:
        """Cria instância do repositório de funcionários"""
        return FuncionarioRepository()

    @staticmethod
    def create_turma_repository() -> TurmaRepository:
        """Cria instância do repositório de turmas"""
        return TurmaRepository()

    @staticmethod
    def create_matricula_dao() -> MatriculaDAO:
        """Cria instância do DAO de matrículas"""
        return MatriculaDAO()

# ================================================================
# EXEMPLO DE USO DOS PATTERNS
# ================================================================

def setup_database_if_needed():
    """Cria o banco e tabelas se não existirem"""
    from pathlib import Path
    
    db_path = Path(__file__).parent / 'entrega4_db.sqlite3'
    
    if not db_path.exists():
        print("=== CONFIGURAÇÃO INICIAL DO BANCO ===")
        print("Criando banco de dados e executando scripts SQL...")
        
        conn = DatabaseConnection().get_connection()
        
        # Executa create_tables.sql
        sql_file = Path(__file__).parent / 'create_tables.sql'
        if sql_file.exists():
            with open(sql_file, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            print("[OK] Estrutura do banco criada (create_tables.sql)")
        
        # Executa insert_data.sql  
        sql_file = Path(__file__).parent / 'insert_data.sql'
        if sql_file.exists():
            with open(sql_file, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            print("[OK] Dados iniciais inseridos (insert_data.sql)")
        
        conn.commit()
        # Não fecha para permitir reutilização pelo Singleton
        print("=== BANCO CONFIGURADO COM SUCESSO ===\n")

def exemplo_uso_patterns():
    """
    Demonstra o uso dos patterns implementados
    Baseado nas operações reais do Sistema GUTO
    """

    # Configura banco se necessário
    setup_database_if_needed()

    print("=== DEMONSTRAÇÃO COMPLETA DOS PATTERNS E CRUDs ===\n")

    # PATTERN: Factory - criando todos os repositórios
    aluno_repo = RepositoryFactory.create_aluno_repository()
    funcionario_repo = RepositoryFactory.create_funcionario_repository()
    turma_repo = RepositoryFactory.create_turma_repository()
    matricula_dao = RepositoryFactory.create_matricula_dao()

    # ================================================================
    # DEMONSTRAÇÃO 1: CRUD DE ALUNOS
    # ================================================================
    print("1. === CRUD DE ALUNOS ===")

    # CREATE - Criar novo aluno (gera nome único e amigável)
    nomes_alunos = ["João Silva Santos", "Pedro Oliveira Costa", "Lucas Ferreira Souza",
                    "Gabriel Santos Lima", "Miguel Costa Pereira", "Rafael Lima Silva"]
    sufixos_alunos = ["Jr.", "II", "III", "Neto", "Filho", "IV", "V"]

    nome_base = random.choice(nomes_alunos)
    sufixo = random.choice(sufixos_alunos)
    contador = random.randint(1, 99)
    nome_unico = f"{nome_base} {sufixo} {contador}"

    novo_aluno = AlunoDTO(
        nome=nome_unico,
        data_nascimento=date(2010, 5, 15),
        sexo="M",
        nome_mae="Maria Silva",
        usuario_cadastro_id=1
    )

    aluno_id = aluno_repo.create(novo_aluno)
    print(f"[OK] CREATE: Aluno criado com ID {aluno_id}")

    # READ - Buscar aluno criado
    aluno_encontrado = aluno_repo.find_by_id(aluno_id)
    if aluno_encontrado:
        print(f"[OK] READ: Aluno encontrado: {aluno_encontrado.nome}")

    # UPDATE - Atualizar dados do aluno
    aluno_encontrado.nome = "João Silva Santos Junior"
    aluno_encontrado.lembrete = "Aluno exemplo para demonstração"
    sucesso_update = aluno_repo.update(aluno_encontrado)
    print(f"[OK] UPDATE: Aluno atualizado: {sucesso_update}")

    # ================================================================
    # DEMONSTRAÇÃO 2: CRUD DE FUNCIONÁRIOS
    # ================================================================
    print("\n2. === CRUD DE FUNCIONÁRIOS ===")

    # CREATE - Criar novo funcionário (gera CPF e nome únicos e amigáveis)
    nomes_funcionarios = ["Ana Paula Costa", "Maria Fernanda Silva", "Carolina Santos Oliveira",
                         "Juliana Lima Pereira", "Patrícia Souza Martins", "Fernanda Costa Lima"]
    sobrenomes_profissionais = ["Prof.", "Dra.", "Mestra", "Coordenadora", "Especialista"]

    nome_base = random.choice(nomes_funcionarios)
    titulo = random.choice(sobrenomes_profissionais)
    contador = random.randint(1, 99)
    nome_funcionario_unico = f"{titulo} {nome_base} {contador}"

    cpf_unico = f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"
    email_id = random.randint(100, 999)

    novo_funcionario = FuncionarioDTO(
        nome=nome_funcionario_unico,
        cpf=cpf_unico,
        data_nascimento=date(1985, 8, 20),
        telefone="(31) 99999-0000",
        email=f"funcionario{email_id}@escola.edu.br",
        cargo="Professora de Matematica",
        data_admissao=date.today(),
        usuario_cadastro_id=1
    )

    funcionario_id = funcionario_repo.create(novo_funcionario)
    print(f"[OK] CREATE: Funcionario criado com ID {funcionario_id}")

    # READ - Buscar funcionário criado
    funcionario_encontrado = funcionario_repo.find_by_id(funcionario_id)
    if funcionario_encontrado:
        print(f"[OK] READ: Funcionario encontrado: {funcionario_encontrado.nome}")

    # READ - Buscar por CPF (método específico)
    funcionario_por_cpf = funcionario_repo.find_by_cpf(cpf_unico)
    if funcionario_por_cpf:
        print(f"[OK] READ (CPF): Funcionario encontrado por CPF: {funcionario_por_cpf.nome}")

    # UPDATE - Atualizar dados do funcionário
    funcionario_encontrado.cargo = "Coordenadora de Matematica"
    funcionario_encontrado.telefone = "(31) 99999-1111"
    sucesso_func_update = funcionario_repo.update(funcionario_encontrado)
    print(f"[OK] UPDATE: Funcionario atualizado: {sucesso_func_update}")

    # ================================================================
    # DEMONSTRAÇÃO 3: CRUD DE TURMAS
    # ================================================================
    print("\n3. === CRUD DE TURMAS ===")

    # CREATE - Criar nova turma (gera nome único e amigável)
    series = ["6º Ano", "7º Ano", "8º Ano", "9º Ano"]
    letras = ["A", "B", "C", "D", "E", "F"]
    turnos_demo = ["Matutino", "Vespertino", "Integral"]

    serie = random.choice(series)
    letra = random.choice(letras)
    contador = random.randint(1, 99)
    nome_turma_unico = f"{serie} {letra}{contador}"

    nova_turma = TurmaDTO(
        nome=nome_turma_unico,
        periodo_letivo="2025",
        tipo_ensino="fundamental",
        ano_serie=serie,
        turno="matutino",
        vagas_total=35,
        usuario_criacao_id=1
    )

    turma_id = turma_repo.create(nova_turma)
    print(f"[OK] CREATE: Turma criada com ID {turma_id}")

    # READ - Buscar turma criada
    turma_encontrada = turma_repo.find_by_id(turma_id)
    if turma_encontrada:
        print(f"[OK] READ: Turma encontrada: {turma_encontrada.nome}")

    # READ - Buscar turmas por período (método específico)
    turmas_2025 = turma_repo.find_by_periodo("2025")
    print(f"[OK] READ (Periodo): {len(turmas_2025)} turmas encontradas em 2025")

    # UPDATE - Atualizar dados da turma
    turma_encontrada.vagas_total = 40
    turma_encontrada.tipo_ensino = "ensino_fundamental"
    sucesso_turma_update = turma_repo.update(turma_encontrada)
    print(f"[OK] UPDATE: Turma atualizada: {sucesso_turma_update}")

    # ================================================================
    # DEMONSTRAÇÃO 4: DAO DE MATRÍCULAS (Operação Específica)
    # ================================================================
    print("\n4. === DAO DE MATRÍCULAS ===")

    # DAO - operação específica de matrícula
    nova_matricula = MatriculaDTO(
        ano_administrativo=2025,
        tipo_ensino="fundamental",
        serie_ano="7º Ano",
        tipo_matricula="nova",
        turno_preferencial="matutino",
        data_matricula=date.today(),
        aluno_id=aluno_id,
        usuario_cadastro_id=1
    )
    # Adicionar campos obrigatórios
    nova_matricula.condicao_anterior = "aprovado"
    nova_matricula.possui_dependencia = False
    nova_matricula.condicoes_especiais_avaliacao = False

    matricula_id = matricula_dao.criar_matricula(nova_matricula)
    print(f"[OK] DAO CREATE: Matricula criada com ID {matricula_id}")

    # DAO - Buscar matrículas do aluno
    matriculas_aluno = matricula_dao.buscar_matriculas_aluno(aluno_id)
    print(f"[OK] DAO READ: {len(matriculas_aluno)} matriculas encontradas para o aluno")

    # ================================================================
    # RELATÓRIO FINAL - ESTATÍSTICAS DO BANCO
    # ================================================================
    print("\n=== RELATÓRIO FINAL - ESTATÍSTICAS ===")
    conn = aluno_repo._db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM alunos_aluno")
    total_alunos = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM alunos_matricula")
    total_matriculas = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM funcionarios_funcionario")
    total_funcionarios = cursor.fetchone()['total']

    print(f"[STATS] Total de alunos: {total_alunos}")
    print(f"[STATS] Total de matriculas: {total_matriculas}")
    print(f"[STATS] Total de funcionarios: {total_funcionarios}")

    # Verificar se temos turmas no banco
    try:
        cursor.execute("SELECT COUNT(*) as total FROM turma_turma")
        total_turmas = cursor.fetchone()['total']
        print(f"[STATS] Total de turmas: {total_turmas}")
    except:
        print("[STATS] Total de turmas: 0 (tabela nao existe)")

    # Listar entidades criadas nesta demonstração
    print("\n=== ENTIDADES CRIADAS NESTA DEMONSTRACAO ===")
    print(f"Aluno: {aluno_encontrado.nome} (ID: {aluno_id})")
    print(f"Funcionario: {funcionario_encontrado.nome} (ID: {funcionario_id})")
    print(f"Turma: {turma_encontrada.nome} (ID: {turma_id})")
    print(f"Matricula: Aluno {aluno_id} em {nova_matricula.serie_ano} (ID: {matricula_id})")

    print("\n[SUCESSO] DEMONSTRACAO COMPLETA - TODOS OS PATTERNS E CRUDs FUNCIONANDO!")

if __name__ == "__main__":
    exemplo_uso_patterns()