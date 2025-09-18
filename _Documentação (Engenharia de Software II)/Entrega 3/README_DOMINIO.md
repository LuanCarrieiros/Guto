# SISTEMA GUTO - CAMADA DE DOMÍNIO

**Disciplina:** Engenharia de Software II
**Entrega:** 3 - Camada de Domínio
**Sistema:** GUTO - Gestão Unificada de Tecnologia Organizacional

**Integrantes do grupo:**
- Luan Barbosa Rosa Carrieiros
- Diego Moreira Rocha
- Arthur Clemente Machado
- Bernardo Ferreira Temponi
- Arthur Gonçalves de Moraes

---

## 📋 **OBJETIVO DA ENTREGA**

Implementar a **camada de domínio** do Sistema GUTO aplicando todos os conceitos de **Orientação a Objetos** discutidos em aula, sem dependências de frameworks (Django, etc.).

---

## 🏗️ **CONCEITOS DE OOP IMPLEMENTADOS**

### ✅ **1. ENCAPSULAMENTO**
- **Atributos privados** (prefixo `__`) para proteger dados internos
- **Atributos protegidos** (prefixo `_`) para herança
- **Propriedades** (@property) para controle de acesso
- **Getters e Setters** com validação

### ✅ **2. HERANÇA**
- **Classe base:** `Pessoa`
- **Classes filhas:** `Aluno` e `Funcionario` herdam de `Pessoa`
- **Reutilização de código** e especialização

### ✅ **3. POLIMORFISMO**
- **Sobrescrita de métodos** (`obter_informacoes_basicas`)
- **Comportamento específico** para cada classe
- **Interface comum** com implementações diferentes

### ✅ **4. COMPOSIÇÃO**
- **Aluno contém** lista de `Responsavel` e `Matricula`
- **Turma contém** lista de `Aluno`
- **Dependência forte** - partes não existem sem o todo

### ✅ **5. AGREGAÇÃO**
- **Aluno pode ter** `TransporteAluno`
- **Turma pode ter** `Funcionario` como professor
- **Dependência fraca** - partes podem existir independentemente

### ✅ **6. ABSTRAÇÃO**
- **Interfaces bem definidas** para cada classe
- **Métodos de negócio** específicos do domínio educacional
- **Ocultação de complexidade** interna

---

## 📚 **DESCRIÇÃO DAS CLASSES**

### 🧑 **Classe `Pessoa` (Classe Base)**
**Arquivo:** `domain_layer.py`, linhas 33-96

**Função:** Classe base abstrata que representa uma pessoa no sistema.

**Atributos principais:**
- `__nome` (privado): Nome da pessoa
- `__data_nascimento` (privado): Data de nascimento
- `__cpf` (privado): CPF da pessoa
- `_data_cadastro` (protegido): Data de cadastro no sistema

**Métodos principais:**
- `@property nome`: Getter para nome com validação
- `@property idade`: Propriedade calculada da idade
- `obter_informacoes_basicas()`: Retorna dados básicos
- `_validar_nome()`, `_validar_cpf()`: Métodos protegidos de validação

**Conceitos demonstrados:**
- ✅ Encapsulamento (atributos privados/protegidos)
- ✅ Propriedades computadas (idade)
- ✅ Métodos de validação

---

### 🎓 **Classe `Aluno` (Herda de Pessoa)**
**Arquivo:** `domain_layer.py`, linhas 99-260

**Função:** Representa um estudante matriculado na escola.

**Atributos específicos:**
- `__codigo` (privado): Código único do aluno
- `__sexo` (privado): Sexo do aluno (M/F)
- `__nome_mae`, `__nome_pai` (privados): Nome dos pais
- `__matriculas` (privado): Lista de matrículas (composição)
- `__responsaveis` (privado): Lista de responsáveis (composição)
- `__transporte` (privado): Transporte escolar (agregação)

**Métodos de negócio:**
- `adicionar_responsavel()`: Adiciona responsável (composição)
- `adicionar_matricula()`: Adiciona matrícula com validação
- `tem_matricula_ativa()`: Verifica matrícula ativa
- `obter_matricula_atual()`: Retorna matrícula vigente
- `arquivar()`: Soft delete do aluno

**Conceitos demonstrados:**
- ✅ Herança (extends Pessoa)
- ✅ Composição (Responsaveis, Matriculas)
- ✅ Agregação (TransporteAluno)
- ✅ Polimorfismo (sobrescreve métodos da classe pai)
- ✅ Regras de negócio educacional

---

### 👨‍🏫 **Classe `Funcionario` (Herda de Pessoa)**
**Arquivo:** `domain_layer.py`, linhas 263-412

**Função:** Representa funcionários da escola (professores, coordenadores, etc.).

**Atributos específicos:**
- `__codigo` (privado): Código único do funcionário
- `__cargo` (privado): Cargo/função do funcionário
- `__telefone`, `__email` (privados): Contatos
- `__data_admissao` (privado): Data de contratação
- `__status` (privado): Status usando Enum

**Métodos de negócio:**
- `admitir()`: Processo de admissão
- `inativar()`: Inativa funcionário
- `colocar_em_licenca()`: Coloca em licença
- `esta_ativo()`: Verifica se está ativo
- `obter_tempo_servico()`: Calcula tempo de trabalho

**Conceitos demonstrados:**
- ✅ Herança (extends Pessoa)
- ✅ Enums para status
- ✅ Métodos de negócio específicos
- ✅ Validações de domínio

---

### 🏫 **Classe `Turma` (Entidade Independente)**
**Arquivo:** `domain_layer.py`, linhas 415-585

**Função:** Representa uma turma/classe escolar.

**Atributos principais:**
- `__nome` (privado): Nome da turma
- `__periodo_letivo` (privado): Ano letivo
- `__tipo_ensino` (privado): Enum do tipo de ensino
- `__turno` (privado): Enum do turno
- `__vagas_total` (privado): Número de vagas
- `__alunos_matriculados` (privado): Lista de alunos (composição)
- `__professor_regente` (privado): Professor da turma (agregação)

**Métodos de negócio:**
- `matricular_aluno()`: Matricula aluno na turma
- `desmatricular_aluno()`: Remove aluno da turma
- `definir_professor_regente()`: Atribui professor
- `fechar_diario()`: Fecha diário da turma
- `esta_lotada()`: Verifica se tem vagas
- `obter_estatisticas()`: Relatório da turma

**Conceitos demonstrados:**
- ✅ Composição (Alunos matriculados)
- ✅ Agregação (Professor regente)
- ✅ Enums para tipos e turnos
- ✅ Métodos complexos de negócio
- ✅ Propriedades calculadas (vagas disponíveis)

---

### 📋 **Classes de Apoio (Composição/Agregação)**

#### **`Responsavel`** - Composição com Aluno
**Função:** Representa responsável legal pelo aluno.
- Existe apenas como parte do aluno
- Contém dados de contato e parentesco

#### **`TransporteAluno`** - Agregação com Aluno
**Função:** Informações de transporte escolar.
- Pode existir independente do aluno
- Pode ser compartilhado entre alunos

#### **`Matricula`** - Composição com Aluno
**Função:** Representa uma matrícula específica.
- Existe apenas como parte do aluno
- Contém dados do período letivo

---

## 🚀 **COMO EXECUTAR**

### **Pré-requisitos:**
- Python 3.8+

### **Execução:**
```bash
cd "_Documentação (Engenharia de Software II)/Entrega 3/"
python domain_layer.py
```

### **Saída Esperada:**
```
=== DEMONSTRAÇÃO DA CAMADA DE DOMÍNIO ===

1. === CRIANDO FUNCIONÁRIO ===
Funcionário criado: Funcionário 1: Ana Paula Costa - Professora De Matematica
Está ativo: True
Tempo de serviço: 231 dias

2. === CRIANDO ALUNO ===
Aluno criado: Aluno 1: João Silva Santos (14 anos)
Responsáveis: 1

3. === CRIANDO TURMA ===
Turma criada: Turma 1: 7º Ano A - 7º Ano (Matutino)
Vagas ocupadas: 1/35

4. === CRIANDO MATRÍCULA ===
Matrícula criada: Matrícula 1: 7º Ano - 2025
Aluno tem matrícula ativa: True

5. === POLIMORFISMO ===
[Demonstração de polimorfismo com informações específicas]

6. === MÉTODOS DE NEGÓCIO ===
[Estatísticas da turma e verificações de regras de negócio]
```

---

## 🎯 **DIFERENCIAIS DA IMPLEMENTAÇÃO**

### **1. Domínio Educacional Real**
- **Regras de negócio** extraídas de sistema real
- **Validações específicas** do contexto escolar
- **Relacionamentos complexos** entre entidades

### **2. OOP Profissional**
- **Todos os conceitos** aplicados corretamente
- **Encapsulamento rigoroso** com validações
- **Herança bem estruturada** com especialização
- **Composição e agregação** claramente definidas

### **3. Código Limpo**
- **Documentação completa** de cada classe
- **Nomenclatura clara** e consistente
- **Métodos de negócio** expressivos
- **Validações robustas**

### **4. Demonstração Completa**
- **Script funcional** que testa todas as classes
- **Exemplo de uso** de cada conceito
- **Saída organizada** e didática

---

## 📝 **RESUMO DOS CONCEITOS APLICADOS**

| Conceito | Implementação | Localização |
|----------|---------------|-------------|
| **Encapsulamento** | Atributos privados (__) e protegidos (_) | Todas as classes |
| **Herança** | Pessoa → Aluno/Funcionario | Linhas 99, 263 |
| **Polimorfismo** | Sobrescrita de obter_informacoes_basicas() | Linhas 240, 390 |
| **Composição** | Aluno ← Responsavel/Matricula | Linhas 150, 180 |
| **Agregação** | Aluno ← TransporteAluno, Turma ← Professor | Linhas 190, 500 |
| **Abstração** | Interfaces bem definidas | Todas as classes |
| **Construtores** | __init__ com validações | Todas as classes |
| **Getters/Setters** | @property com validações | Todas as classes |
| **Métodos de Negócio** | Regras específicas educacionais | Linhas 200+, 350+, 520+ |

---

## ✅ **STATUS: ENTREGA COMPLETA**

**Todos os requisitos atendidos:**
- ✅ Classes principais do domínio implementadas
- ✅ Atributos e métodos conforme modelagem
- ✅ Relacionamentos (composição/agregação) definidos
- ✅ Encapsulamento adequado (private/protected/public)
- ✅ Construtores e métodos de acesso implementados
- ✅ Métodos de negócio com regras educacionais
- ✅ Código organizado e bem documentado
- ✅ README explicativo completo

**Resultado:** Camada de domínio **profissional** e **funcional** do Sistema GUTO!