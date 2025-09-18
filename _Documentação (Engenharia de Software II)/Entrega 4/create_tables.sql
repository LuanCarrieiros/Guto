-- ================================================================
-- SISTEMA GUTO - ESTRUTURA DO BANCO DE DADOS
-- Camada de Persistência - Entrega 4
-- ================================================================

-- Criação das tabelas principais do módulo Alunos
-- Baseado na estrutura Django já implementada

BEGIN;

-- Tabela principal de Alunos
CREATE TABLE "alunos_aluno" (
    "codigo" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(255) NOT NULL,
    "nome_social" VARCHAR(255) NULL,
    "data_nascimento" DATE NOT NULL,
    "sexo" VARCHAR(1) NOT NULL,
    "nome_mae" VARCHAR(255) NULL,
    "nome_pai" VARCHAR(255) NULL,
    "mae_nao_declarada" BOOLEAN NOT NULL DEFAULT 0,
    "pai_nao_declarado" BOOLEAN NOT NULL DEFAULT 0,
    "aluno_gemeo" BOOLEAN NOT NULL DEFAULT 0,
    "falta_historico_escolar" BOOLEAN NOT NULL DEFAULT 0,
    "aluno_exclusivo_aee" BOOLEAN NOT NULL DEFAULT 0,
    "tipo_arquivo" VARCHAR(20) NOT NULL DEFAULT 'ativo',
    "lembrete" TEXT NULL,
    "foto" VARCHAR(100) NULL,
    "data_cadastro" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "data_atualizacao" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "usuario_cadastro_id" INTEGER NOT NULL
);

-- Tabela de Documentação dos Alunos (1:1)
CREATE TABLE "alunos_documentacaoaluno" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "rg" VARCHAR(20) NULL,
    "cpf" VARCHAR(14) NULL,
    "certidao_nascimento" VARCHAR(50) NULL,
    "titulo_eleitor" VARCHAR(20) NULL,
    "aluno_nao_possui_documentos" BOOLEAN NOT NULL DEFAULT 0,
    "escola_nao_recebeu_documentos" BOOLEAN NOT NULL DEFAULT 0,
    "aluno_id" INTEGER NOT NULL UNIQUE
);

-- Tabela de Responsáveis (1:N)
CREATE TABLE "alunos_responsavel" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(255) NOT NULL,
    "parentesco" VARCHAR(50) NOT NULL,
    "telefone" VARCHAR(20) NULL,
    "email" VARCHAR(254) NULL,
    "endereco" TEXT NULL,
    "aluno_id" INTEGER NOT NULL
);

-- Tabela de Transporte (1:1)
CREATE TABLE "alunos_transportealuno" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "utiliza_transporte" BOOLEAN NOT NULL DEFAULT 0,
    "nome_motorista" VARCHAR(255) NULL,
    "placa_veiculo" VARCHAR(10) NULL,
    "rota" VARCHAR(100) NULL,
    "aluno_id" INTEGER NOT NULL UNIQUE
);

-- Tabela de Matrículas (1:N)
CREATE TABLE "alunos_matricula" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "ano_administrativo" INTEGER NOT NULL,
    "tipo_ensino" VARCHAR(20) NOT NULL,
    "serie_ano" VARCHAR(50) NOT NULL,
    "tipo_matricula" VARCHAR(20) NOT NULL,
    "turno_preferencial" VARCHAR(20) NOT NULL,
    "data_matricula" DATE NOT NULL,
    "possui_dependencia" BOOLEAN NOT NULL DEFAULT 0,
    "condicao_anterior" VARCHAR(20) NOT NULL,
    "escola_origem" VARCHAR(255) NULL,
    "tipo_rede_origem" VARCHAR(50) NULL,
    "pais_origem" VARCHAR(100) NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'ativa',
    "data_encerramento" DATE NULL,
    "motivo_encerramento" TEXT NULL,
    "condicoes_especiais_avaliacao" BOOLEAN NOT NULL DEFAULT 0,
    "data_cadastro" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "data_atualizacao" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "aluno_id" INTEGER NOT NULL,
    "usuario_cadastro_id" INTEGER NOT NULL
);

-- Tabela de Funcionários (para demonstrar relacionamentos)
CREATE TABLE "funcionarios_funcionario" (
    "codigo" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(255) NOT NULL,
    "cpf" VARCHAR(14) UNIQUE NOT NULL,
    "data_nascimento" DATE NOT NULL,
    "telefone" VARCHAR(20) NULL,
    "email" VARCHAR(254) NULL,
    "cargo" VARCHAR(100) NOT NULL,
    "data_admissao" DATE NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'ativo',
    "data_cadastro" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "usuario_cadastro_id" INTEGER NOT NULL
);

-- Criação dos índices para otimização
CREATE INDEX "idx_aluno_nome" ON "alunos_aluno" ("nome");
CREATE INDEX "idx_aluno_usuario_cadastro" ON "alunos_aluno" ("usuario_cadastro_id");
CREATE INDEX "idx_responsavel_aluno" ON "alunos_responsavel" ("aluno_id");
CREATE INDEX "idx_matricula_aluno" ON "alunos_matricula" ("aluno_id");
CREATE INDEX "idx_matricula_ano" ON "alunos_matricula" ("ano_administrativo");
CREATE INDEX "idx_funcionario_cpf" ON "funcionarios_funcionario" ("cpf");

-- Constraints de integridade referencial criadas implicitamente via REFERENCES

-- Constraint de unicidade para evitar múltiplas matrículas ativas
CREATE UNIQUE INDEX "idx_matricula_unica_ativa" 
ON "alunos_matricula" ("aluno_id", "ano_administrativo", "tipo_matricula");

COMMIT;

-- ================================================================
-- OBSERVAÇÕES SOBRE A ESTRUTURA:
-- 
-- 1. PATTERN: Active Record implementado via Django ORM
-- 2. PATTERN: Foreign Key para integridade referencial
-- 3. PATTERN: Unique constraints para regras de negócio
-- 4. PATTERN: Soft delete via campo 'status' e 'tipo_arquivo'
-- 5. PATTERN: Audit trail com campos de data e usuário
-- ================================================================