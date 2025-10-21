# DOCUMENTAÇÃO DE INTERFACE - SISTEMA GUTO
## Descrição Detalhada das Telas Principais

**Sistema:** GUTO - Gestão Unificada de Tecnologia Organizacional
**Entrega:** 5 - Protótipo de Interface
**Disciplina:** Engenharia de Software II

---

## 📋 ÍNDICE DE TELAS

1. [Tela de Login](#1-tela-de-login)
2. [Dashboard Principal](#2-dashboard-principal)
3. [Módulo Alunos](#3-módulo-alunos)
4. [Módulo Funcionários](#4-módulo-funcionários)
5. [Módulo Turmas](#5-módulo-turmas)
6. [Diário Eletrônico](#6-diário-eletrônico)
7. [Telas Auxiliares](#7-telas-auxiliares)

---

## 1. TELA DE LOGIN

### 📄 **Arquivo:** `templates/registration/login.html`

### 🎯 **Objetivo:**
Autenticar usuários no sistema GUTO, fornecendo acesso seguro às funcionalidades de acordo com o perfil (secretário, professor, coordenador).

### 🎨 **Elementos Visuais:**

#### **Header:**
- Logo circular com ícone de escola (`fa-school`)
- Título "GUTO" em branco (text-4xl, font-bold)
- Subtítulo "Sistema de Gestão Escolar" (text-blue-100)
- Fundo com gradiente azul-roxo (`from-guto-blue to-guto-purple`)

#### **Card de Login:**
- Card centralizado (max-w-md, rounded-2xl)
- Título de boas-vindas "Bem-vindo!" (text-2xl)
- Instruções "Faça login para acessar o sistema"

#### **Formulário:**
- **Campo Usuário:**
  - Label com ícone de usuário (`fa-user`)
  - Input text com placeholder "Digite seu usuário"
  - Border focus azul (`focus:ring-guto-blue`)

- **Campo Senha:**
  - Label com ícone de cadeado (`fa-lock`)
  - Input password com placeholder "Digite sua senha"
  - Autocomplete "current-password"

- **Opções Adicionais:**
  - Checkbox "Lembrar-me"
  - Link "Esqueceu a senha?" (text-guto-blue)

- **Botão de Login:**
  - Gradiente azul-roxo com efeito hover
  - Ícone de login (`fa-sign-in-alt`)
  - Texto "Entrar"
  - Efeito scale ao hover

#### **Mensagens de Erro:**
- Exibidas em card vermelho-claro (`bg-red-50`)
- Ícone de aviso (`fa-exclamation-triangle`)
- Texto descritivo do erro

#### **Footer:**
- Copyright com ano dinâmico
- Versão do sistema (1.0)
- Texto em azul-claro

### 🔄 **Fluxo de Navegação:**
```
Login (usuário/senha)
    ↓
[Validação Django Auth]
    ↓
Success → Dashboard Principal
    ↓
Error → Mensagem de erro + permanece na tela
```

### 💻 **Interatividade:**
- Animação de entrada do card (fade + translateY)
- Labels mudam de cor ao focar inputs
- Validação client-side e server-side
- Efeitos hover nos botões e links

### 📱 **Responsividade:**
- Card adapta largura em mobile (w-full com padding)
- Formulário empilha verticalmente
- Logo e títulos mantêm proporções

---

## 2. DASHBOARD PRINCIPAL

### 📄 **Arquivo:** `templates/dashboard/home.html`

### 🎯 **Objetivo:**
Fornecer uma visão geral do sistema com estatísticas em tempo real, ações rápidas e atividades recentes, servindo como hub central de navegação.

### 🎨 **Elementos Visuais:**

#### **Header de Boas-Vindas:**
- Card com gradiente azul-roxo (`from-blue-600 to-purple-600`)
- Saudação "Bem-vindo ao GUTO!"
- Subtítulo "Sistema de Gestão Educacional"
- Data e hora atualizadas em tempo real
- Ícone de escola no canto direito

#### **Cards de Estatísticas (Grid 4 colunas):**

1. **Total de Alunos:**
   - Ícone: `fa-user-graduate` (azul)
   - Número grande com total de alunos
   - Label "Alunos Cadastrados"
   - Border-left azul (border-blue-500)

2. **Total de Funcionários:**
   - Ícone: `fa-users` (verde)
   - Número de funcionários ativos
   - Label "Funcionários Ativos"
   - Border-left verde (border-green-500)

3. **Avaliações Pendentes:**
   - Ícone: `fa-clipboard-list` (laranja)
   - Contador de avaliações pendentes
   - Label "Avaliações Pendentes"
   - Border-left laranja (border-orange-500)

4. **Rotas de Transporte:**
   - Ícone: `fa-bus` (roxo)
   - Número de rotas ativas
   - Label "Rotas de Transporte"
   - Border-left roxo (border-purple-500)

#### **Seção de Distribuição por Turma:**
- Título "Distribuição por Turma" com ícone (`fa-chart-bar`)
- Contador de turmas ativas
- Lista de turmas com:
  - Nome da série/turma
  - Número de alunos matriculados
  - Barra de progresso visual (bg-blue-600)
  - Percentual de ocupação

#### **Ações Rápidas:**
- Grid 6 colunas com botões visuais
- Cada card contém:
  - Ícone colorido específico
  - Label da ação
  - Hover effect (border muda de cor, background suave)

**Ações disponíveis:**
- Turmas (azul)
- Diário (verde)
- Alunos (laranja)
- Funcionários (roxo)
- Relatórios (índigo)
- Conceitos (teal)

#### **Painel de Atividade Recente:**
- Lista de últimas atividades do sistema
- Cada item mostra:
  - Ícone da ação (azul)
  - Descrição da atividade
  - Tempo relativo ("X minutos atrás")
- Scroll vertical para histórico extenso

#### **Status do Sistema:**
- Indicador de status online (bolinha verde)
- Ícones de banco de dados e servidor
- Label "Online"

### 🔄 **Fluxo de Navegação:**
```
Dashboard
    ├→ Alunos (card ou ação rápida)
    ├→ Funcionários (card ou ação rápida)
    ├→ Turmas (card ou ação rápida)
    ├→ Diário (ação rápida)
    ├→ Relatórios (ação rápida)
    └→ Conceitos (ação rápida)
```

### 💻 **Interatividade:**
- Relógio atualizado a cada segundo via JavaScript
- Cards de estatísticas com hover effect (translateY)
- Barras de progresso animadas
- Scroll suave no painel de atividades

### 📱 **Responsividade:**
- Grid de estatísticas: 1 col (mobile) → 4 cols (desktop)
- Ações rápidas: 2 cols (mobile) → 6 cols (desktop)
- Layout: 1 coluna (mobile) → 3 colunas (desktop)

---

## 3. MÓDULO ALUNOS

### 📄 **Arquivos Principais:**
- `templates/alunos/aluno_list.html` - Listagem
- `templates/alunos/aluno_form.html` - Cadastro/Edição
- `templates/alunos/aluno_detail.html` - Detalhes

---

### 3.1 LISTA DE ALUNOS

### 🎯 **Objetivo:**
Gerenciar todos os alunos cadastrados com busca avançada, filtros e ações em massa.

### 🎨 **Elementos Visuais:**

#### **Header:**
- Título "Gestão de Alunos" (text-3xl, font-bold)
- Subtítulo explicativo
- Botão "Novo Aluno" com ícone (`fa-plus`)

#### **Filtros de Pesquisa:**
- Card cinza-claro (bg-gray-50) com formulário
- **Busca por:**
  - Select com opções (Nome, Código)
  - Input text para termo de busca
  - Layout flexível (flex-wrap)

- **Filtro de Arquivo:**
  - Select com opções: Todos, Corrente, Permanente

- **Filtro Aluno Gêmeo:**
  - Checkbox para filtrar gêmeos

- **Botões de Ação:**
  - "Buscar" (azul, `fa-search`)
  - "Limpar" (cinza, `fa-times`)

#### **Estatísticas Rápidas (Grid 4 colunas):**
- Total de Alunos (azul)
- Arquivo Corrente (verde)
- Arquivo Permanente (amarelo)
- Alunos Gêmeos (roxo)

#### **Tabela de Resultados:**
- Header com colunas:
  - Código
  - Nome
  - Data de Nascimento
  - Idade
  - Série
  - Status
  - Ações

- Cada linha contém:
  - Dados do aluno
  - Badge de status (ativo/inativo)
  - Botões de ação:
    - Visualizar (azul, `fa-eye`)
    - Editar (amarelo, `fa-edit`)
    - Excluir (vermelho, `fa-trash`)

#### **Paginação:**
- Controles de navegação entre páginas
- Indicador de página atual
- Total de resultados

### 🔄 **Fluxo de Navegação:**
```
Lista de Alunos
    ├→ Novo Aluno → Formulário de Cadastro
    ├→ Visualizar → Detalhes do Aluno
    ├→ Editar → Formulário de Edição
    └→ Excluir → Modal de Confirmação → Lista atualizada
```

---

### 3.2 FORMULÁRIO DE ALUNO

### 🎯 **Objetivo:**
Cadastrar ou editar informações completas de um aluno, incluindo dados pessoais, documentação, responsáveis e transporte.

### 🎨 **Elementos Visuais:**

#### **Título Dinâmico:**
- "Cadastrar Novo Aluno" ou "Editar Aluno: [Nome]"

#### **Sistema de Abas:**
Formulário dividido em seções lógicas:

**Aba 1 - Dados Pessoais:**
- Nome Completo (5 colunas)
- Data de Nascimento (2 colunas)
- Sexo (1 coluna - select M/F)
- Cor/Raça (2 colunas - select)
- Nacionalidade (2 colunas)
- Naturalidade (3 colunas)
- UF Nascimento (1 coluna)
- Nome da Mãe (5 colunas)
- Nome do Pai (5 colunas)
- Foto do Aluno (upload de imagem)

**Aba 2 - Endereço:**
- CEP (2 colunas)
- Endereço (4 colunas)
- Número (2 colunas)
- Complemento (2 colunas)
- Bairro (3 colunas)
- Cidade (3 colunas)
- UF (1 coluna - select)
- Zona de Residência (select: Urbana/Rural)

**Aba 3 - Documentação:**
- RG (2 colunas)
- Órgão Emissor (2 colunas)
- Data de Emissão (2 colunas)
- CPF (2 colunas)
- Certidão de Nascimento (3 colunas)
- Tipo Sanguíneo (1 coluna)
- Possui Deficiência (checkbox)
- Tipo de Deficiência (textarea)

**Aba 4 - Responsáveis:**
- Nome do Responsável (4 colunas)
- CPF (2 colunas)
- Telefone (2 colunas)
- Email (4 colunas)
- Grau de Parentesco (2 colunas)
- Botão "Adicionar Responsável" para múltiplos

**Aba 5 - Transporte:**
- Utiliza Transporte Escolar (checkbox)
- Ponto de Embarque (3 colunas)
- Ponto de Desembarque (3 colunas)
- Distância da Escola (2 colunas)
- Tipo de Veículo (2 colunas)

#### **Botões de Ação:**
- "Salvar" (verde, `fa-save`)
- "Cancelar" (cinza, `fa-times`)
- "Voltar" (azul, `fa-arrow-left`)

### 💻 **Validações:**
- Campos obrigatórios com asterisco vermelho
- Validação de CPF (máscara e dígitos verificadores)
- Validação de CEP (8 dígitos)
- Data de nascimento não pode ser futura
- Foto com limite de tamanho (2MB)

### 🔄 **Fluxo de Navegação:**
```
Formulário de Aluno
    ├→ Salvar → Validação → Success → Lista de Alunos
    ├→ Salvar → Validação → Error → Mensagens de erro no form
    ├→ Cancelar → Confirmação → Lista de Alunos
    └→ Voltar → Página anterior (navegação inteligente)
```

---

### 3.3 DETALHES DO ALUNO

### 🎯 **Objetivo:**
Visualizar todas as informações do aluno de forma organizada e permitir ações relacionadas (matrícula, histórico, impressão).

### 🎨 **Elementos Visuais:**

#### **Header:**
- Foto do aluno (se houver)
- Nome completo em destaque
- Código do aluno
- Badge de status (Ativo/Inativo)

#### **Seção de Informações (Cards):**

**Card 1 - Dados Pessoais:**
- Data de Nascimento e Idade calculada
- Sexo, Cor/Raça
- Nacionalidade, Naturalidade
- Nome dos pais

**Card 2 - Endereço:**
- Endereço completo formatado
- CEP, Bairro, Cidade/UF
- Zona de residência

**Card 3 - Documentação:**
- RG, CPF
- Certidão de Nascimento
- Tipo Sanguíneo
- Deficiências (se houver)

**Card 4 - Responsáveis:**
- Lista de responsáveis com:
  - Nome, CPF, Telefone
  - Grau de parentesco
  - Email de contato

**Card 5 - Transporte:**
- Informações de transporte escolar
- Pontos de embarque/desembarque
- Tipo de veículo

**Card 6 - Matrículas:**
- Histórico de matrículas
- Ano letivo
- Série/Turma
- Status da matrícula
- Botão "Nova Matrícula"

#### **Ações Disponíveis:**
- Editar Aluno (amarelo, `fa-edit`)
- Imprimir Ficha (azul, `fa-print`)
- Mover para Arquivo (laranja, `fa-archive`)
- Excluir Aluno (vermelho, `fa-trash`)
- Voltar (cinza, `fa-arrow-left`)

### 🔄 **Fluxo de Navegação:**
```
Detalhes do Aluno
    ├→ Editar → Formulário de Edição
    ├→ Imprimir → Gera PDF com ficha completa
    ├→ Nova Matrícula → Formulário de Matrícula
    ├→ Mover para Arquivo → Confirmação → Status atualizado
    ├→ Excluir → Confirmação → Lista de Alunos
    └→ Voltar → Lista de Alunos
```

---

## 4. MÓDULO FUNCIONÁRIOS

### 📄 **Arquivos Principais:**
- `templates/funcionarios/funcionario_list.html` - Listagem
- `templates/funcionarios/funcionario_form.html` - Cadastro/Edição
- `templates/funcionarios/funcionario_detail.html` - Detalhes

---

### 4.1 LISTA DE FUNCIONÁRIOS

### 🎯 **Objetivo:**
Gerenciar funcionários (professores e administrativos) com filtros por função, status e busca.

### 🎨 **Elementos Visuais:**

#### **Header:**
- Título "Gestão de Funcionários"
- Subtítulo "Cadastro e controle de pessoal"
- Botão "Novo Funcionário" (roxo, `fa-plus`)

#### **Filtros:**
- Busca por: Nome, Código, Matrícula
- Filtro por Função: Todos, Professor, Coordenador, Secretário
- Filtro por Status: Todos, Ativos, Inativos
- Botões: Buscar, Limpar

#### **Tabela:**
- Colunas:
  - Código
  - Nome
  - Matrícula
  - Função
  - Data de Admissão
  - Status
  - Ações

- Badges coloridos por função:
  - Professor: azul
  - Coordenador: roxo
  - Secretário: verde

#### **Ações por Linha:**
- Visualizar (azul)
- Editar (amarelo)
- Excluir (vermelho)

### 🔄 **Fluxo:**
```
Lista de Funcionários
    ├→ Novo → Formulário
    ├→ Visualizar → Detalhes
    ├→ Editar → Formulário preenchido
    └→ Excluir → Confirmação
```

---

### 4.2 FORMULÁRIO DE FUNCIONÁRIO

### 🎯 **Objetivo:**
Cadastrar funcionário com dados pessoais, funcionais, habilitações e escolaridade.

### 🎨 **Sistema de Abas:**

**Aba 1 - Dados Pessoais:**
- Nome Completo (5 cols)
- CPF (2 cols), RG (2 cols)
- Data de Nascimento (2 cols)
- Sexo (1 col), Estado Civil (2 cols)
- Nacionalidade, Naturalidade
- Endereço completo
- Telefones e Email
- Foto

**Aba 2 - Dados Funcionais:**
- Matrícula (2 cols)
- Função (3 cols - select)
- Data de Admissão (2 cols)
- Carga Horária Semanal (2 cols)
- Salário (2 cols)
- Tipo de Contrato (2 cols)
- Status (Ativo/Inativo)

**Aba 3 - Habilitações:**
- Curso de Graduação (4 cols)
- Instituição (3 cols)
- Ano de Conclusão (2 cols)
- Registro Profissional (3 cols)
- Botão "Adicionar Habilitação"

**Aba 4 - Escolaridade:**
- Nível: Fundamental, Médio, Superior, Pós
- Curso/Área
- Instituição
- Situação (Completo/Cursando/Incompleto)

**Aba 5 - Disciplinas (se Professor):**
- Selecionar disciplinas que leciona
- Checkboxes para múltiplas disciplinas

### 💻 **Validações:**
- CPF válido
- Matrícula única
- Data de admissão não futura
- Carga horária entre 20-40h
- Salário > 0

### 🔄 **Fluxo:**
```
Formulário
    ├→ Salvar → Validação → Lista
    └→ Cancelar → Confirmação → Lista
```

---

## 5. MÓDULO TURMAS

### 📄 **Arquivos Principais:**
- `templates/turma/turmas_list.html` - Listagem
- `templates/turma/turma_form.html` - Cadastro/Edição
- `templates/turma/turma_detail.html` - Detalhes
- `templates/turma/enturmar_alunos.html` - Enturmação

---

### 5.1 LISTA DE TURMAS

### 🎯 **Objetivo:**
Visualizar todas as turmas ativas com informações de ocupação e acesso rápido.

### 🎨 **Elementos:**

#### **Cards de Turmas (Grid):**
Cada card exibe:
- Nome da Turma (ex: "1º Ano A")
- Ano Letivo (2025)
- Série/Etapa
- Total de Alunos / Vagas
- Barra de progresso de ocupação
- Badge com percentual

**Cores por ocupação:**
- Verde: < 70%
- Amarelo: 70-90%
- Vermelho: > 90%

#### **Ações por Card:**
- Visualizar Detalhes
- Enturmar Alunos
- Gerenciar Disciplinas
- Editar Turma

#### **Header:**
- Botão "Nova Turma" (amarelo, `fa-plus`)
- Contador de turmas ativas

### 🔄 **Fluxo:**
```
Lista de Turmas
    ├→ Nova Turma → Formulário
    ├→ Detalhes → Informações + Alunos enturmados
    ├→ Enturmar → Seleção de alunos
    └→ Disciplinas → Gestão de matérias
```

---

### 5.2 ENTURMAÇÃO DE ALUNOS

### 🎯 **Objetivo:**
Vincular alunos a uma turma específica com validação de vagas e pré-requisitos.

### 🎨 **Elementos:**

#### **Informações da Turma:**
- Nome da turma em destaque
- Vagas disponíveis (visual)
- Série/etapa esperada

#### **Lista de Alunos Disponíveis:**
- Tabela com:
  - Checkbox de seleção
  - Código do aluno
  - Nome completo
  - Idade
  - Série atual

#### **Filtros:**
- Apenas alunos compatíveis com a série
- Apenas alunos sem turma ativa
- Busca por nome

#### **Painel de Selecionados:**
- Contador de alunos marcados
- Validação de vagas em tempo real
- Aviso se exceder limite

#### **Botões:**
- "Enturmar Selecionados" (verde, desabilitado se exceder vagas)
- "Cancelar" (cinza)

### 💻 **Validações:**
- Não pode exceder vagas disponíveis
- Aluno não pode ter duas turmas ativas
- Idade compatível com série (warning)

### 🔄 **Fluxo:**
```
Enturmação
    ├→ Selecionar alunos
    ├→ Validar vagas
    ├→ Confirmar → Success → Detalhes da Turma
    └→ Cancelar → Volta sem salvar
```

---

## 6. DIÁRIO ELETRÔNICO

### 📄 **Arquivos Principais:**
- `templates/diario/diario_home.html` - Dashboard do Diário
- `templates/diario/diario_turma.html` - Diário de uma turma
- `templates/diario/fazer_chamada_diario.html` - Registro de presença
- `templates/diario/lancar_notas_diario.html` - Lançamento de notas

---

### 6.1 DASHBOARD DO DIÁRIO

### 🎯 **Objetivo:**
Hub central para professores acessarem diários das turmas que lecionam.

### 🎨 **Elementos:**

#### **Header Vibrante:**
- Gradiente colorido com emojis
- Título "Diário Eletrônico" com ícone de livro
- Saudação ao professor logado
- Data atual

#### **Cards de Turmas/Disciplinas:**
Grid de cards, cada um com:
- Emoji da disciplina (📚📐🔬🌍)
- Nome da disciplina
- Turma
- Total de alunos
- Última atualização
- Badge de status (em dia/atrasado)

**Ações por card:**
- Fazer Chamada (verde, `fa-check`)
- Lançar Notas (azul, `fa-edit`)
- Ver Diário Completo (roxo, `fa-book`)

#### **Estatísticas Rápidas:**
- Total de turmas
- Alunos total
- Aulas lançadas na semana
- Avaliações pendentes

### 🔄 **Fluxo:**
```
Dashboard Diário
    ├→ Fazer Chamada → Tela de presença
    ├→ Lançar Notas → Tela de notas
    └→ Ver Diário → Diário completo da turma
```

---

### 6.2 FAZER CHAMADA

### 🎯 **Objetivo:**
Registrar presença/ausência dos alunos em uma aula específica.

### 🎨 **Elementos:**

#### **Header:**
- Disciplina e Turma
- Data da aula (selecionável)
- Hora de início/fim

#### **Lista de Alunos:**
Tabela com:
- Número (ordem)
- Foto do aluno (se houver)
- Nome completo
- Botões de presença:
  - "P" (verde, presente)
  - "F" (vermelho, falta)
  - "FJ" (laranja, falta justificada)

**Estado visual:**
- Botão selecionado fica destacado
- Linha muda de cor conforme status
- Ícones visuais (✓, ✗, ⚠)

#### **Resumo:**
- Total de presentes
- Total de faltas
- Percentual de presença

#### **Botões de Ação:**
- "Salvar Chamada" (verde)
- "Marcar Todos Presentes" (azul)
- "Cancelar" (cinza)

### 💻 **Interatividade:**
- Atualização em tempo real do resumo
- Confirmação antes de salvar
- Avisos se houver campos não marcados

### 🔄 **Fluxo:**
```
Fazer Chamada
    ├→ Selecionar data
    ├→ Marcar presença/falta para cada aluno
    ├→ Salvar → Validação → Dashboard Diário
    └→ Cancelar → Descarta alterações
```

---

### 6.3 LANÇAR NOTAS

### 🎯 **Objetivo:**
Registrar notas de avaliações para os alunos de uma turma/disciplina.

### 🎨 **Elementos:**

#### **Seleção de Avaliação:**
- Select com avaliações criadas:
  - Nome da avaliação (ex: "Prova Bimestral")
  - Data da avaliação
  - Peso
  - Valor máximo

- Botão "Nova Avaliação" para criar

#### **Tabela de Notas:**
Colunas:
- Nº
- Nome do Aluno
- Input numérico para nota
- Conceito (calculado automaticamente)
- Observações (textarea pequena)

**Validações visuais:**
- Border vermelha se nota > valor máximo
- Border verde se nota aprovação
- Border amarela se nota recuperação
- Nota calculada em tempo real

#### **Estatísticas da Avaliação:**
- Média da turma (calculada dinamicamente)
- Maior nota
- Menor nota
- Aprovados / Reprovados
- Gráfico de distribuição de notas

#### **Botões:**
- "Salvar Notas" (verde, `fa-save`)
- "Exportar para Excel" (azul, `fa-file-excel`)
- "Imprimir Relatório" (roxo, `fa-print`)
- "Voltar" (cinza)

### 💻 **Validações:**
- Nota entre 0 e valor máximo
- Conceito calculado automaticamente
- Destaque para alunos em recuperação
- Aviso se houver notas não lançadas

### 🔄 **Fluxo:**
```
Lançar Notas
    ├→ Selecionar avaliação
    ├→ Preencher notas
    ├→ Salvar → Validação → Confirmação → Dashboard
    └→ Nova Avaliação → Form de criação → Volta para lançamento
```

---

### 6.4 DIÁRIO COMPLETO DA TURMA

### 🎯 **Objetivo:**
Visão consolidada de todas as aulas, presenças e notas de uma turma em uma disciplina.

### 🎨 **Elementos:**

#### **Header:**
- Nome da disciplina
- Turma
- Professor
- Período letivo

#### **Sistema de Abas:**

**Aba 1 - Frequência:**
- Calendário mensal com aulas marcadas
- Tabela com:
  - Data da aula
  - Conteúdo ministrado
  - Total de presentes/faltas
  - Ações (editar chamada)

**Aba 2 - Avaliações:**
- Lista de avaliações criadas
- Para cada avaliação:
  - Nome e data
  - Estatísticas (média, aprovados)
  - Botão para lançar/editar notas

**Aba 3 - Alunos:**
- Lista de alunos enturmados
- Para cada aluno:
  - Nome e código
  - Percentual de presença
  - Média geral
  - Status (aprovado/recuperação/reprovado)

**Aba 4 - Relatórios:**
- Botões para gerar relatórios:
  - Mapa de frequência
  - Boletim da turma
  - Relatório de desempenho
  - Ata de resultados

#### **Gráficos:**
- Gráfico de barras: Distribuição de notas
- Gráfico de linha: Evolução da média ao longo do tempo
- Gráfico de pizza: Percentual de aprovação

### 🔄 **Fluxo:**
```
Diário Completo
    ├→ Visualizar frequência → Editar chamada específica
    ├→ Ver avaliações → Editar notas
    ├→ Ver alunos → Detalhes individuais
    └→ Gerar relatórios → PDF/Excel
```

---

## 7. TELAS AUXILIARES

### 7.1 TELA "EM DESENVOLVIMENTO"

### 📄 **Arquivo:** `templates/em_desenvolvimento.html`

### 🎯 **Objetivo:**
Informar ao usuário que a funcionalidade ainda não está disponível.

### 🎨 **Elementos:**
- Ícone grande de construção (`fa-hard-hat`)
- Título "Funcionalidade em Desenvolvimento"
- Nome da funcionalidade solicitada
- Mensagem explicativa
- Botão "Voltar ao Dashboard"
- Ilustração amigável

### 🔄 **Fluxo:**
```
Módulo não implementado → Em Desenvolvimento → Voltar ao Dashboard
```

---

### 7.2 MODAIS DE CONFIRMAÇÃO

### 🎯 **Objetivo:**
Confirmar ações destrutivas antes de executá-las.

### 🎨 **Elementos:**

#### **Modal de Exclusão:**
- Fundo escurecido (overlay)
- Card centralizado
- Ícone de aviso (vermelho, `fa-exclamation-triangle`)
- Título "Confirmar Exclusão"
- Mensagem: "Tem certeza que deseja excluir [ITEM]?"
- Aviso: "Esta ação não pode ser desfeita"
- Botões:
  - "Confirmar" (vermelho)
  - "Cancelar" (cinza)

#### **Modal de Desenturmação:**
- Similar ao de exclusão
- Campos adicionais:
  - Motivo da desenturmação (select)
  - Observações (textarea)
- Validação de campos obrigatórios

### 🔄 **Fluxo:**
```
Ação destrutiva → Modal de confirmação
    ├→ Confirmar → Executa ação → Mensagem de sucesso
    └→ Cancelar → Fecha modal sem executar
```

---

### 7.3 SISTEMA DE MENSAGENS

### 🎯 **Objetivo:**
Exibir feedback visual de ações realizadas pelo usuário.

### 🎨 **Tipos de Mensagens:**

#### **Sucesso (verde):**
- Background: `bg-green-100`
- Texto: `text-green-800`
- Ícone: `fa-check-circle`
- Exemplo: "Aluno cadastrado com sucesso!"

#### **Erro (vermelho):**
- Background: `bg-red-100`
- Texto: `text-red-800`
- Ícone: `fa-times-circle`
- Exemplo: "Erro ao salvar. Verifique os campos."

#### **Aviso (amarelo):**
- Background: `bg-yellow-100`
- Texto: `text-yellow-800`
- Ícone: `fa-exclamation-triangle`
- Exemplo: "Atenção: Turma quase cheia!"

#### **Informação (azul):**
- Background: `bg-blue-100`
- Texto: `text-blue-800`
- Ícone: `fa-info-circle`
- Exemplo: "Dados carregados com sucesso"

### 💻 **Comportamento:**
- Exibidas no topo da página
- Auto-dismiss após 5 segundos (opcional)
- Botão de fechar manual (×)
- Animação de entrada/saída

---

## 📊 RESUMO DE FLUXOS DE NAVEGAÇÃO

### **Fluxo Principal do Sistema:**

```
Login
  ↓
Dashboard
  ├→ Alunos
  │   ├→ Lista → Detalhes → Editar → Lista
  │   ├→ Lista → Novo → Formulário → Lista
  │   └→ Lista → Excluir → Confirmação → Lista
  │
  ├→ Funcionários
  │   ├→ Lista → Detalhes → Editar → Lista
  │   └→ Lista → Novo → Formulário → Lista
  │
  ├→ Turmas
  │   ├→ Lista → Detalhes → Enturmar → Detalhes
  │   └→ Lista → Nova → Formulário → Lista
  │
  ├→ Diário
  │   ├→ Dashboard → Fazer Chamada → Dashboard
  │   ├→ Dashboard → Lançar Notas → Dashboard
  │   └→ Dashboard → Diário Completo → Dashboard
  │
  └→ Outros Módulos → Em Desenvolvimento → Dashboard
```

### **Sistema de Navegação Inteligente:**
- Todas as telas têm botão "Voltar"
- JavaScript rastreia histórico real do usuário
- Voltar sempre leva à página anterior visitada
- Fallback para dashboard se não houver histórico

---

## 🎨 PADRÕES VISUAIS RECORRENTES

### **Cards:**
- Background branco (`bg-white`)
- Sombras suaves (`shadow-lg`, `shadow-xl`)
- Bordas arredondadas (`rounded-lg`, `rounded-xl`)
- Padding consistente (`p-4`, `p-6`)
- Border colorida à esquerda para categorização

### **Botões:**
- Primários: Gradiente ou cor sólida
- Sempre com ícone + texto
- Estados: normal, hover, active, disabled
- Tamanhos: sm, md, lg
- Efeitos: scale, shadow ao hover

### **Formulários:**
- Labels acima dos campos
- Campos com border cinza (`border-gray-300`)
- Focus ring azul (`focus:ring-blue-500`)
- Mensagens de erro abaixo do campo
- Campos obrigatórios com asterisco vermelho
- Grid responsivo (Tailwind columns)

### **Tabelas:**
- Header com fundo cinza (`bg-gray-50`)
- Zebra striping em linhas (`odd:bg-gray-50`)
- Hover effect em linhas
- Ações sempre na última coluna
- Responsivas com scroll horizontal em mobile

### **Badges:**
- Arredondados (`rounded-full`)
- Tamanho pequeno (`text-xs`, `px-2`, `py-1`)
- Cores semânticas:
  - Verde: ativo/aprovado
  - Vermelho: inativo/reprovado
  - Amarelo: pendente/em recuperação
  - Azul: informativo
  - Roxo: especial

---

## 💻 RECURSOS DE INTERATIVIDADE

### **JavaScript Implementado:**

1. **navigation.js** (181 linhas):
   - Gerenciamento de histórico
   - Botões voltar inteligentes
   - Persistência em sessionStorage

2. **Scripts inline nos templates:**
   - Relógio em tempo real (dashboard)
   - Validação de formulários
   - Cálculos automáticos (idade, médias)
   - Máscaras de input (CPF, CEP, telefone)

3. **HTMX:**
   - Requisições AJAX sem page reload
   - Atualização parcial de conteúdo
   - Polling para atualizações em tempo real

4. **Alpine.js:**
   - Componentes reativos leves
   - Dropdowns e modals
   - Estados locais de componentes

### **Animações CSS:**
- Transições suaves (`transition-all duration-300`)
- Hover effects (scale, shadow, color)
- Fade in/out de mensagens
- Skeleton loading em listas

---

## 📱 RESPONSIVIDADE DETALHADA

### **Breakpoints e Adaptações:**

#### **Mobile (<640px):**
- Sidebar oculta/colapsada
- Grid: 1 coluna
- Tabelas: scroll horizontal
- Formulários: campos full-width
- Ações: botões empilhados

#### **Tablet (640px-1024px):**
- Sidebar visível mas estreita
- Grid: 2 colunas
- Tabelas: scroll horizontal seletivo
- Formulários: 2 colunas

#### **Desktop (>1024px):**
- Sidebar fixa à esquerda (288px)
- Grid: 3-4 colunas
- Tabelas: full-width sem scroll
- Formulários: grid otimizado (até 6 colunas)

---

## ✅ CHECKLIST DE COBERTURA

### **Telas Documentadas:**
- [x] Login
- [x] Dashboard Principal
- [x] Lista de Alunos
- [x] Formulário de Aluno
- [x] Detalhes do Aluno
- [x] Lista de Funcionários
- [x] Formulário de Funcionário
- [x] Lista de Turmas
- [x] Enturmação de Alunos
- [x] Dashboard do Diário
- [x] Fazer Chamada
- [x] Lançar Notas
- [x] Diário Completo
- [x] Tela Em Desenvolvimento
- [x] Modais de Confirmação
- [x] Sistema de Mensagens

### **Elementos Documentados:**
- [x] Identidade visual (cores, fontes, ícones)
- [x] Padrões de componentes (cards, botões, forms, tabelas)
- [x] Fluxos de navegação
- [x] Validações e interatividade
- [x] Responsividade
- [x] Sistema de navegação inteligente

---

## 🎯 CONCLUSÃO

Esta documentação apresenta **todas as telas principais do sistema GUTO**, detalhando:

✅ **Objetivo de cada tela** - Por que existe e qual problema resolve
✅ **Elementos visuais** - Componentes, cores, tipografia, layout
✅ **Fluxos de navegação** - Como o usuário se move entre telas
✅ **Interatividade** - Validações, animações, comportamentos dinâmicos
✅ **Responsividade** - Como a tela se adapta a diferentes dispositivos

O protótipo implementado vai muito além de wireframes estáticos, sendo um **sistema web completo e funcional** que demonstra excelência em **design de interface**, **usabilidade** e **experiência do usuário**.

---

**Desenvolvido para Entrega 5 - Protótipo de Interface**
**Disciplina: Engenharia de Software II**
**Sistema GUTO - Gestão Unificada de Tecnologia Organizacional**
