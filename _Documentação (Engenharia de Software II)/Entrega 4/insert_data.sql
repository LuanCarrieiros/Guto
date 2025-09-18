-- ================================================================
-- SISTEMA GUTO - DADOS INICIAIS DO BANCO
-- Camada de Persistência - Dados de Exemplo
-- ================================================================

BEGIN;

-- Inserção de dados de exemplo para demonstração
-- Baseado nos dados reais do sistema em funcionamento

-- Dados de exemplo para Funcionários (usuários do sistema)
INSERT INTO "funcionarios_funcionario" 
("codigo", "nome", "cpf", "data_nascimento", "telefone", "email", "cargo", "data_admissao", "status", "data_cadastro", "usuario_cadastro_id") 
VALUES 
(1, 'Maria Silva Santos', '123.456.789-01', '1985-03-15', '(31) 99999-1234', 'maria.silva@escola.edu.br', 'Diretora', '2023-02-01', 'ativo', datetime('now'), 1),
(2, 'João Carlos Pereira', '987.654.321-02', '1978-07-22', '(31) 99999-5678', 'joao.pereira@escola.edu.br', 'Coordenador Pedagógico', '2022-08-15', 'ativo', datetime('now'), 1),
(3, 'Ana Beatriz Costa', '456.789.123-03', '1990-11-08', '(31) 99999-9012', 'ana.costa@escola.edu.br', 'Professora', '2024-03-10', 'ativo', datetime('now'), 1);

-- Dados de exemplo para Alunos
INSERT INTO "alunos_aluno" 
("codigo", "nome", "nome_social", "data_nascimento", "sexo", "nome_mae", "nome_pai", "mae_nao_declarada", "pai_nao_declarado", "aluno_gemeo", "falta_historico_escolar", "aluno_exclusivo_aee", "tipo_arquivo", "lembrete", "foto", "data_cadastro", "data_atualizacao", "usuario_cadastro_id") 
VALUES 
(1, 'Lucas Henrique Silva', NULL, '2010-05-20', 'M', 'Fernanda Silva Santos', 'Carlos Henrique Silva', 0, 0, 0, 0, 0, 'ativo', NULL, NULL, datetime('now'), datetime('now'), 1),
(2, 'Sophia Maria Oliveira', NULL, '2009-09-15', 'F', 'Claudia Maria Santos', 'Roberto Oliveira Lima', 0, 0, 0, 0, 0, 'ativo', NULL, NULL, datetime('now'), datetime('now'), 1),
(3, 'Gabriel dos Santos Costa', NULL, '2011-01-10', 'M', 'Juliana dos Santos', 'Marcos Costa Pereira', 0, 0, 0, 0, 0, 'ativo', NULL, NULL, datetime('now'), datetime('now'), 1),
(4, 'Emanuelle Rodrigues', 'Emy', '2010-12-03', 'F', 'Patricia Rodrigues Silva', 'Eduardo Rodrigues', 0, 0, 0, 0, 0, 'ativo', 'Aluna com necessidades especiais de atenção', NULL, datetime('now'), datetime('now'), 1),
(5, 'Pedro Augusto Lima', NULL, '2008-04-25', 'M', 'Vanessa Lima Souza', 'Augusto Lima Junior', 0, 0, 0, 0, 0, 'ativo', NULL, NULL, datetime('now'), datetime('now'), 1);

-- Documentação dos Alunos
INSERT INTO "alunos_documentacaoaluno" 
("id", "rg", "cpf", "certidao_nascimento", "titulo_eleitor", "aluno_nao_possui_documentos", "escola_nao_recebeu_documentos", "aluno_id") 
VALUES 
(1, '1234567-1', NULL, '123456789012345', NULL, 0, 0, 1),
(2, '2345678-2', NULL, '234567890123456', NULL, 0, 0, 2),
(3, '3456789-3', NULL, '345678901234567', NULL, 0, 0, 3),
(4, '4567890-4', NULL, '456789012345678', NULL, 0, 0, 4),
(5, '5678901-5', '123.456.789-05', '567890123456789', NULL, 0, 0, 5);

-- Responsáveis
INSERT INTO "alunos_responsavel" 
("id", "nome", "parentesco", "telefone", "email", "endereco", "aluno_id") 
VALUES 
(1, 'Fernanda Silva Santos', 'Mãe', '(31) 98765-4321', 'fernanda.silva@email.com', 'Rua das Flores, 123 - Centro', 1),
(2, 'Carlos Henrique Silva', 'Pai', '(31) 98765-4322', 'carlos.silva@email.com', 'Rua das Flores, 123 - Centro', 1),
(3, 'Claudia Maria Santos', 'Mãe', '(31) 98765-5432', 'claudia.santos@email.com', 'Av. Principal, 456 - Jardim', 2),
(4, 'Juliana dos Santos', 'Mãe', '(31) 98765-6543', 'juliana.santos@email.com', 'Rua da Escola, 789 - Vila Nova', 3),
(5, 'Patricia Rodrigues Silva', 'Mãe', '(31) 98765-7654', 'patricia.rodrigues@email.com', 'Rua do Colégio, 321 - Centro', 4),
(6, 'Vanessa Lima Souza', 'Mãe', '(31) 98765-8765', 'vanessa.lima@email.com', 'Av. dos Estudantes, 654 - Bela Vista', 5);

-- Transporte
INSERT INTO "alunos_transportealuno" 
("id", "utiliza_transporte", "nome_motorista", "placa_veiculo", "rota", "aluno_id") 
VALUES 
(1, 1, 'José da Silva', 'ABC-1234', 'Rota Centro', 1),
(2, 0, NULL, NULL, NULL, 2),
(3, 1, 'Maria Fernandes', 'DEF-5678', 'Rota Vila Nova', 3),
(4, 1, 'José da Silva', 'ABC-1234', 'Rota Centro', 4),
(5, 0, NULL, NULL, NULL, 5);

-- Matrículas
INSERT INTO "alunos_matricula" 
("id", "ano_administrativo", "tipo_ensino", "serie_ano", "tipo_matricula", "turno_preferencial", "data_matricula", "possui_dependencia", "condicao_anterior", "escola_origem", "tipo_rede_origem", "pais_origem", "status", "data_encerramento", "motivo_encerramento", "condicoes_especiais_avaliacao", "data_cadastro", "data_atualizacao", "aluno_id", "usuario_cadastro_id") 
VALUES 
(1, 2025, 'fundamental', '7º Ano', 'nova', 'matutino', '2025-08-01', 0, 'aprovado', 'E.M. Santos Dumont', 'publica', 'Brasil', 'ativa', NULL, NULL, 0, datetime('now'), datetime('now'), 1, 1),
(2, 2025, 'fundamental', '8º Ano', 'nova', 'matutino', '2025-08-01', 0, 'aprovado', 'E.E. Dom Pedro II', 'publica', 'Brasil', 'ativa', NULL, NULL, 0, datetime('now'), datetime('now'), 2, 1),
(3, 2025, 'fundamental', '6º Ano', 'nova', 'vespertino', '2025-08-05', 0, 'aprovado', 'E.M. José de Alencar', 'publica', 'Brasil', 'ativa', NULL, NULL, 0, datetime('now'), datetime('now'), 3, 1),
(4, 2025, 'fundamental', '7º Ano', 'transferencia', 'matutino', '2025-09-15', 0, 'transferido', 'Colégio Particular ABC', 'privada', 'Brasil', 'ativa', NULL, NULL, 1, datetime('now'), datetime('now'), 4, 1),
(5, 2025, 'medio', '1º Ano', 'nova', 'matutino', '2025-08-01', 0, 'aprovado', 'E.E. Machado de Assis', 'publica', 'Brasil', 'ativa', NULL, NULL, 0, datetime('now'), datetime('now'), 5, 1);

COMMIT;

-- ================================================================
-- OBSERVAÇÕES SOBRE OS DADOS:
-- 
-- 1. Dados seguem regras de negócio do sistema real
-- 2. Relacionamentos 1:1 e 1:N implementados corretamente
-- 3. Campos obrigatórios e opcionais respeitados
-- 4. Dados coerentes com cenário escolar brasileiro
-- 5. IDs de usuário referenciam administrador padrão (id=1)
-- ================================================================