# ENTREGA 4 - IMPLEMENTAÇÃO DA CAMADA DE PERSISTÊNCIA

**Sistema:** GUTO - Gestão Unificada de Tecnologia Organizacional  
**Disciplina:** Engenharia de Software II  
**Período:** 2025.2  

**Integrantes do grupo:** 
- Luan Barbosa Rosa Carrieiros
- Diego Moreira Rocha
- Arthur Clemente Machado
- Bernardo Ferreira Temponi
- Arthur Gonçalves de Moraes

---

## 📋 **CONTEÚDO DA ENTREGA**

### 1. **Scripts SQL**
- 📄 `create_tables.sql` - Criação da estrutura do banco (DDL)
- 📄 `insert_data.sql` - Povoamento inicial com dados (DML)

### 2. **Código-fonte da Camada de Persistência**
- 🐍 `repository_layer.py` - Implementação completa dos Repositórios e DAOs

### 3. **Documentação**
- 📖 `Analise_Patterns_Persistencia.md` - Análise completa dos patterns de projeto
- 📖 `README.md` - Guia da entrega

---

## 🎯 **OBJETIVOS ATENDIDOS**

✅ **Scripts SQL para criação do banco** (create_tables.sql)  
✅ **Scripts SQL para povoamento inicial** (insert_data.sql)  
✅ **Implementação de Repositórios CRUD** (repository_layer.py)  
✅ **Documentação de Padrões de Projeto** (Analise_Patterns_Persistencia.md)  
✅ **Boas práticas de organização** (estrutura modular e comentada)  

---

## 🏗️ **ARQUITETURA IMPLEMENTADA**

### **Padrões de Projeto Utilizados:**

1. **🔄 Active Record** - Django ORM (modelo base do sistema)
2. **📚 Repository** - Abstração para operações CRUD 
3. **🗃️ DAO (Data Access Object)** - Operações específicas de domínio
4. **🔒 Singleton** - Controle de conexão única com banco
5. **📦 DTO (Data Transfer Object)** - Transferência de dados entre camadas
6. **🏭 Factory** - Criação padronizada de repositórios

### **Tecnologias:**
- **Backend:** Python 3.x + SQLite3
- **Framework Base:** Django 5.2.5 (sistema principal)
- **Paradigma:** Orientação a Objetos com Patterns

---

## 🚀 **COMO EXECUTAR**

### **Pré-requisitos:**
- Python 3.8+
- SQLite3 (incluído no Python)

### **Execução:**

```bash
# 1. Navegar para a pasta da entrega
cd "_Documentação/Entrega 4/"

# 2. Executar demonstração dos patterns
python repository_layer.py
# ou no Linux/WSL:
python3 repository_layer.py
```

**Nota:** O banco de dados SQLite é criado automaticamente na primeira execução usando os scripts SQL fornecidos.

### **Saída Esperada (primeira execução):**
```
=== CONFIGURAÇÃO INICIAL DO BANCO ===
Criando banco de dados e executando scripts SQL...
[OK] Estrutura do banco criada (create_tables.sql)
[OK] Dados iniciais inseridos (insert_data.sql)
=== BANCO CONFIGURADO COM SUCESSO ===

Aluno criado com ID: 6
Aluno encontrado: João Silva Santos
Matrícula criada com ID: 6

=== ESTATÍSTICAS ATUAIS DO BANCO ===
Total de alunos no banco: 6
Total de matrículas no banco: 6
```

**Execuções subsequentes** mostrarão apenas a demonstração dos patterns (sem recriar o banco).

---

## 📊 **ESTRUTURA DO BANCO DE DADOS**

### **Tabelas Principais:**
- `alunos_aluno` - Dados principais dos estudantes
- `alunos_documentacaoaluno` - Documentos dos alunos (1:1)
- `alunos_responsavel` - Responsáveis pelos alunos (1:N)
- `alunos_transportealuno` - Informações de transporte (1:1)
- `alunos_matricula` - Matrículas dos alunos (1:N)
- `funcionarios_funcionario` - Dados dos funcionários

### **Relacionamentos:**
- **1:1** - Aluno ↔ Documentação, Aluno ↔ Transporte
- **1:N** - Aluno → Responsáveis, Aluno → Matrículas
- **Constraints** - Chaves estrangeiras e índices únicos

---

## 💡 **DIFERENCIAIS DA IMPLEMENTAÇÃO**

### **1. Baseado em Sistema Real**
- Extraído do Sistema GUTO Django em produção
- Regras de negócio reais da gestão escolar
- Dados coerentes com cenário educacional brasileiro

### **2. Patterns Profissionais**
- Implementação robusta dos padrões solicitados
- Código comentado e bem estruturado
- Separação clara de responsabilidades

### **3. Funcionalidade Completa**
- CRUD completo para todas as entidades
- Validações de regras de negócio
- Tratamento de erros e transações

### **4. Documentação Técnica**
- Análise detalhada de cada pattern
- Exemplos de código com explicações
- Justificativas técnicas para cada escolha

---

## 🎓 **APRENDIZADOS E BENEFÍCIOS**

### **Técnicos:**
- **Separação de Responsabilidades** - Cada classe tem papel bem definido
- **Testabilidade** - Repositórios podem ser facilmente mockados
- **Manutenibilidade** - Código organizado facilita evolução
- **Reusabilidade** - Patterns permitem reutilização em outros contextos

### **Educacionais:**
- Aplicação prática de padrões de projeto
- Compreensão da importância da camada de persistência
- Experiência com arquitetura multicamadas
- Boas práticas de desenvolvimento de software

---

## 📝 **CONSIDERAÇÕES FINAIS**

Esta entrega demonstra a implementação **profissional** da camada de persistência, extraída de um sistema Django **real e funcional**. Os padrões foram adaptados para mostrar os conceitos solicitados, mantendo a robustez e as boas práticas do sistema original.

**Pontos Fortes:**
- ✅ Código baseado em sistema em produção
- ✅ Implementação completa dos patterns solicitados  
- ✅ Documentação técnica detalhada
- ✅ Scripts SQL funcionais e bem estruturados
- ✅ Arquitetura escalável e manutenível

**Status:** ✅ **ENTREGA COMPLETA E FUNCIONAL**