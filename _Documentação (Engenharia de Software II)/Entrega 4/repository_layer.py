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
    
    # PATTERN: Factory - criando repositórios
    aluno_repo = RepositoryFactory.create_aluno_repository()
    matricula_dao = RepositoryFactory.create_matricula_dao()
    
    # PATTERN: DTO - criando objeto de transferência
    novo_aluno = AlunoDTO(
        nome="João Silva Santos",
        data_nascimento=date(2010, 5, 15),
        sexo="M",
        nome_mae="Maria Silva",
        usuario_cadastro_id=1
    )
    
    # PATTERN: Repository - operações CRUD
    aluno_id = aluno_repo.create(novo_aluno)
    print(f"Aluno criado com ID: {aluno_id}")
    
    # Buscar aluno criado
    aluno_encontrado = aluno_repo.find_by_id(aluno_id)
    if aluno_encontrado:
        print(f"Aluno encontrado: {aluno_encontrado.nome}")
    
    # PATTERN: DAO - operação específica de matrícula
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
    # Adicionar campos obrigatórios que faltaram no DTO
    nova_matricula.condicao_anterior = "aprovado"
    nova_matricula.possui_dependencia = False
    nova_matricula.condicoes_especiais_avaliacao = False
    
    matricula_id = matricula_dao.criar_matricula(nova_matricula)
    print(f"Matrícula criada com ID: {matricula_id}")
    
    # Mostrar estatísticas e listagem completa
    print("\n=== ESTATÍSTICAS ATUAIS DO BANCO ===")
    conn = aluno_repo._db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM alunos_aluno")
    total_alunos = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM alunos_matricula")
    total_matriculas = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM funcionarios_funcionario")
    total_funcionarios = cursor.fetchone()['total']
    
    print(f"Total de alunos: {total_alunos}")
    print(f"Total de matrículas: {total_matriculas}")
    print(f"Total de funcionários: {total_funcionarios}")
    
    # Listar todos os alunos
    print("\n=== TODOS OS ALUNOS CADASTRADOS ===")
    cursor.execute("SELECT codigo, nome, data_nascimento FROM alunos_aluno ORDER BY codigo")
    alunos = cursor.fetchall()
    for aluno in alunos:
        print(f"ID {aluno['codigo']}: {aluno['nome']} (nascido em {aluno['data_nascimento']})")
    
    # Listar todos os funcionários
    print("\n=== TODOS OS FUNCIONÁRIOS CADASTRADOS ===")
    cursor.execute("SELECT codigo, nome, cargo FROM funcionarios_funcionario ORDER BY codigo")
    funcionarios = cursor.fetchall()
    for funcionario in funcionarios:
        print(f"ID {funcionario['codigo']}: {funcionario['nome']} - {funcionario['cargo']}")

if __name__ == "__main__":
    exemplo_uso_patterns()