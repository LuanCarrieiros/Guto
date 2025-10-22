# 🎓 Sistema GUTO - Gestão Unificada e Tecnológica Organizacional

Sistema completo de gestão escolar desenvolvido em Django para controle de alunos, funcionários, turmas, avaliações, diário eletrônico e demais módulos educacionais.

---

## 🚀 Como Executar o Projeto

### 📋 **Pré-requisitos**
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 🔧 **Instalação e Execução**

#### **Windows**
```powershell
# 1. Extrair o projeto e navegar até a pasta
cd caminho\para\Guto

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar ambiente virtual
venv\Scripts\activate

# 4. Se houver erro de execução de scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 5. Instalar dependências
pip install -r requirements.txt

# 6. Executar o servidor
python manage.py runserver
```

#### **Linux/Mac**
```bash
# 1. Extrair o projeto e navegar até a pasta
cd caminho/para/Guto

# 2. Criar ambiente virtual
python3 -m venv venv

# 3. Ativar ambiente virtual
source venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar o servidor
python manage.py runserver
```

### 🌐 **Acessar o Sistema**

1. Abrir navegador em: **http://localhost:8000** ou **http://127.0.0.1:8000**
2. Fazer login com as credenciais:
   - **Usuário**: (verifique o banco de dados ou crie um superusuário)
   - **Senha**: (idem)

#### **Criar Superusuário (se necessário)**
```bash
python manage.py createsuperuser
```

---

## 📊 Status do Projeto

### ✅ **Módulos Completamente Funcionais**

| Módulo | Status | Funcionalidades |
|--------|--------|-----------------|
| **📚 Alunos** | ✅ 100% | CRUD completo, matrículas, documentação, responsáveis, transporte |
| **👨‍🏫 Funcionários** | ✅ 90% | CRUD completo, filtros avançados, gestão de cargos e habilitações |
| **🏠 Dashboard** | ✅ 100% | Estatísticas, atividades recentes, visão geral do sistema |
| **📖 Diário Eletrônico** | ✅ 95% | Sistema completo de chamada, lançamento de notas, gestão de avaliações |
| **🎓 Turmas/Avaliação** | ✅ 95% | Gestão de turmas, enturmação, conceitos, avaliações |

### 🟡 **Módulos Parcialmente Implementados**

| Módulo | Status | Observações |
|--------|--------|-------------|
| **🎯 AEE** | 🟡 60% | Dashboard funcional, necessita templates CRUD |
| **🔧 Opções** | 🟡 50% | Calendário escolar básico, sistema de relatórios inicial |
| **🏫 Escola** | 🟡 40% | Gestão de itinerários formativos implementada |
| **📊 Censo** | 🟡 40% | Relatórios básicos, necessita exportação |

### 🔴 **Módulos Estruturados (Aguardando Implementação)**

| Módulo | Status | Observações |
|--------|--------|-------------|
| **⚙️ Utilitários** | 🟡 30% | Models completos, necessita interface administrativa |
| **🚌 Transporte** | 🔴 10% | Models prontos, aguarda implementação de views |
| **📖 Programas** | 🔴 10% | Models prontos, aguarda implementação de views |

---

## 🎨 Principais Funcionalidades Implementadas

### 📚 **Sistema de Diário Eletrônico**
- ✅ **Navegação em 5 Etapas**: Fluxo intuitivo de seleção (Turma → Disciplina → Período → Diário → Ações)
- ✅ **Indicador de Progresso Visual**: Bolinhas e barras coloridas mostrando a etapa atual
- ✅ **Breadcrumb Completo**: Navegação contextual em todas as páginas
- ✅ **Fazer Chamada por Disciplina**: Registro de presença/ausência específico por matéria
- ✅ **Lançamento de Notas**: Sistema de múltiplas avaliações com validações
- ✅ **Gerenciamento de Avaliações**: CRUD completo integrado ao diário
- ✅ **Relatório de Avaliações**: Visão geral das avaliações da disciplina
- ✅ **Alturas Padronizadas**: Todas as páginas com estrutura visual consistente

### 🎓 **Sistema de Enturmação**
- ✅ **Constraint de Unicidade**: Um aluno só pode estar ativo em uma turma por vez
- ✅ **Sistema de Transferência**: Confirmação prévia antes de transferir aluno
- ✅ **Preservação de Histórico**: Enturmações anteriores mantidas como registro
- ✅ **Interface Intuitiva**: Feedback claro sobre ações e consequências

### 👥 **Gestão de Alunos**
- ✅ **CRUD Completo**: Cadastro, edição, consulta, exclusão e impressão
- ✅ **Sistema de Matrículas**: Gestão completa do ciclo de matrícula
- ✅ **Arquivo Permanente**: Movimentação de alunos inativos
- ✅ **Documentação Completa**: Gestão de documentos, responsáveis e transporte
- ✅ **Validações Avançadas**: Regras de negócio implementadas

### 👨‍🏫 **Gestão de Funcionários**
- ✅ **Cadastro Completo**: Dados pessoais, funcionais e documentação
- ✅ **Busca Avançada**: Filtros por nome, código, matrícula, função e status
- ✅ **Sistema de Abas**: Organização em abas (Dados, Documentação, Funcionais, etc.)
- ✅ **Validações**: Unicidade de matrícula, campos obrigatórios
- ✅ **Layout Responsivo**: Formulários otimizados para diferentes telas

---

## 🏗️ Arquitetura Técnica

### **Backend**
- **Framework**: Django 5.2.6
- **Database**: SQLite (incluído no projeto com dados de demonstração)
- **Autenticação**: Sistema Django Auth completo
- **Apps**: dashboard, alunos, funcionarios, turma, diario, opcoes, aee, escola, transporte, programa, utilitarios, censo

### **Frontend**
- **CSS Framework**: Tailwind CSS 3.x
- **JavaScript**: Vanilla JS com validações client-side
- **Templates**: Django Template Engine
- **Ícones**: Font Awesome 6.x
- **Design**: Interface moderna com gradientes e emojis

### **Estrutura de Diretórios**
```
Guto/
├── alunos/           # Módulo de gestão de alunos
├── funcionarios/     # Módulo de gestão de funcionários
├── turma/            # Módulo de turmas e enturmação
├── diario/           # Módulo de diário eletrônico
├── dashboard/        # Dashboard principal
├── opcoes/           # Configurações e relatórios
├── aee/              # Atendimento Educacional Especializado
├── escola/           # Gestão escolar e curricular
├── transporte/       # Transporte escolar (estruturado)
├── programa/         # Programas pedagógicos (estruturado)
├── utilitarios/      # Utilitários do sistema
├── censo/            # Relatórios censitários
├── templates/        # Templates HTML
├── static/           # Arquivos estáticos (CSS, JS, imagens)
├── media/            # Arquivos de upload (fotos, documentos)
├── guto_system/      # Configurações do projeto
├── db.sqlite3        # Banco de dados (incluído com dados de teste)
├── manage.py         # Gerenciador Django
└── requirements.txt  # Dependências do projeto
```

---

## 📝 Dados de Demonstração

O banco de dados **db.sqlite3** incluído no projeto já contém:
- ✅ Usuários de teste
- ✅ Alunos cadastrados
- ✅ Turmas configuradas
- ✅ Disciplinas e professores
- ✅ Avaliações e notas de exemplo
- ✅ Enturmações realizadas

Isso permite testar o sistema imediatamente após a instalação!

---

## 🎯 Requisitos Funcionais Atendidos

### **Módulo Alunos (100%)**
- ✅ RF101-RF108: Cadastro completo de alunos
- ✅ RF201-RF209: Sistema de matrículas
- ✅ RNF101-RNF205: Todas as regras de negócio

### **Módulo Funcionários (90%)**
- ✅ RF403-RF511: Gestão de funcionários
- ✅ RNF401-RNF408: Validações e regras

### **Módulo Diário Eletrônico (95%)**
- ✅ RF701-RF705: Sistema completo de diário
- ✅ Chamada por disciplina
- ✅ Lançamento de notas e avaliações
- ✅ Relatórios e visualizações

### **Módulo Enturmação (100%)**
- ✅ RF301-RF310: Sistema de enturmação
- ✅ Transferências controladas
- ✅ Preservação de histórico

---

## 🔒 Regras de Negócio Principais

### **Enturmação**
- **RN-ENT001**: Um aluno só pode estar ativo em uma turma por vez
- **RN-ENT002**: Transferência entre turmas preserva histórico escolar
- **RN-ENT003**: Sistema solicita confirmação antes de transferir aluno

### **Diário Eletrônico**
- **RN-DIARIO001**: Cada disciplina tem avaliações próprias e isoladas
- **RN-DIARIO002**: Chamada é obrigatoriamente por disciplina específica
- **RN-DIARIO003**: Notas vinculadas a avaliação+aluno+disciplina+turma

### **Alunos**
- **RN-ALU001**: Nome completo obrigatório
- **RN-ALU002**: CPF único no sistema
- **RN-ALU003**: Validação de datas (nascimento < matrícula)

---

## 📚 Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.8+ | Linguagem base |
| Django | 5.2.6 | Framework web |
| SQLite | 3.x | Banco de dados |
| Tailwind CSS | 3.x | Estilização |
| Font Awesome | 6.x | Ícones |
| JavaScript | ES6+ | Interatividade |

---

## 🎓 Desenvolvido por

**Projeto Acadêmico - Sistema de Gestão Escolar**

Este sistema foi desenvolvido como projeto acadêmico, implementando conceitos de:
- Engenharia de Software
- Desenvolvimento Web com Django
- Arquitetura MVC/MVT
- Banco de Dados Relacional
- Interface Responsiva
- UX/UI Design
- Regras de Negócio Educacional

---

## 📞 Suporte

Para dúvidas sobre a execução do projeto:
1. Verifique se todas as dependências foram instaladas corretamente
2. Certifique-se de que o ambiente virtual está ativado
3. Confirme que o Python 3.8+ está instalado
4. Execute `python manage.py migrate` se houver problemas com o banco

---

## 📄 Licença

Este é um projeto acadêmico desenvolvido para fins educacionais.

---

**Sistema GUTO** - Gestão Escolar Moderna e Eficiente 🚀
