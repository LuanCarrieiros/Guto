# 🎓 Sistema GUTO - Gestão Unificada e Tecnológica Organizacional

Sistema completo de gestão escolar desenvolvido em Django para controle de alunos, funcionários, turmas, avaliações, diário eletrônico e demais módulos educacionais.

---

## 🚀 Como Executar o Projeto

### 📋 **Pré-requisitos**
- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### 🔧 **Instalação e Execução**

#### **Windows**
```powershell
# 1. Navegar até a pasta do projeto
cd caminho\para\Guto

# 2. Criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate
# (se houver erro de execução de scripts:)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Instalar dependências, aplicar migrações e executar
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### **Linux/Mac**
```bash
cd caminho/para/Guto
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 🌐 **Acessar o Sistema**

1. Abrir o navegador em **http://127.0.0.1:8000**
2. Entrar com um usuário existente no banco de demonstração ou criar um administrador:
   ```bash
   python manage.py createsuperuser
   ```
3. A administração do Django fica em **/admin** (todos os cadastros dos módulos estão registrados lá).

### 🎲 **Dados de demonstração**
O banco incluído já vem populado. Para recriar os dados de exemplo dos módulos complementares
(transporte, AEE, itinerários, programas, calendário, grupos e instituições) em outro banco:
```bash
python manage.py popular_demonstracao
```
O comando pode ser executado várias vezes sem duplicar registros.

### 🧪 **Testes**
```bash
python manage.py test
```
Inclui um teste de navegação (`dashboard/tests_navegacao.py`) que entra como administrador,
percorre todas as páginas alcançáveis pelos links e falha se alguma responder com erro.

### ⚙️ **Configuração para produção**
As configurações sensíveis vêm de variáveis de ambiente (com valores de desenvolvimento como padrão):

| Variável | Padrão | Uso |
|----------|--------|-----|
| `DJANGO_SECRET_KEY` | chave de desenvolvimento | **Obrigatório** definir em produção |
| `DJANGO_DEBUG` | `True` | Use `False` em produção |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Domínios separados por vírgula |

---

## 📊 Status do Projeto

Todos os módulos do menu lateral estão implementados e acessíveis:

| Módulo | Funcionalidades |
|--------|-----------------|
| **🏠 Dashboard** | Estatísticas gerais, alunos por turma, atividades recentes |
| **📚 Alunos** | CRUD, cadastro completo em abas (identificação, documentação, responsáveis, transporte e dados adicionais personalizados), matrículas, arquivo permanente, impressão |
| **👨‍🏫 Funcionários** | CRUD, cadastro completo em abas (habilitações, disciplinas e deficiências incluídas), busca antes do cadastro, arquivo permanente, impressão de lista e de folha de frequência, associação de professores e outros profissionais às turmas |
| **🎓 Turmas** | Turmas, disciplinas, enturmação, avaliações, conceitos, bimestres/períodos e relatórios (boletim por aluno, frequência e desempenho da turma) |
| **📖 Diário Eletrônico** | Fluxo Turma → Disciplina → Período, chamada, lançamento de notas, avaliações, parecer descritivo, recuperação especial e fechamento do diário (diário fechado não aceita alterações) |
| **🛣️ Itinerários (Escola)** | Itinerários formativos, unidades curriculares, grade do itinerário e enturmação com controle de vagas |
| **🎯 AEE** | Projetos pedagógicos, turmas de AEE/Atividade Complementar, enturmação com controle de vagas e histórico |
| **📘 Programas** | Programas pedagógicos, módulos, inscrição de participantes, aulas, frequência, avaliações e cálculo da nota final |
| **🚌 Transporte** | Rotas, pontos de parada, veículos, manutenções, motoristas, alunos transportados, registro de viagens e relatório mensal |
| **📊 Censo** | Censo escolar por ano, relatórios de matrículas/funcionários/estatísticas e exportação em CSV ou JSON |
| **🔧 Opções** | Calendário escolar com eventos (visualização e impressão) e emissão de relatórios de turmas com filtros |
| **⚙️ Utilitários** | Usuários, grupos de acesso e permissões por módulo, instituições, transferências, tipos de avaliação, dados adicionais, configurações, bloqueios de funcionalidade e auditoria |

### 🔐 Controle de acesso
- **Utilitários** é restrito a administradores (superusuário ou acesso à área administrativa).
- **Permissões de grupo**: em *Utilitários › Grupos*, cada grupo pode ter regras por módulo (visualizar, incluir, alterar, excluir). Módulos sem regra ficam liberados.
- **Bloqueios de funcionalidade**: impedem inclusões, alterações ou exclusões em um módulo durante um período (direto, por ano administrativo ou por tipo de ensino).
- **Auditoria**: logins, logouts e toda alteração bem-sucedida nos módulos são registrados automaticamente.

### 🧮 Critérios de aprovação
Boletins e relatórios usam média mínima **6,0** e frequência mínima **75%**. Os valores podem ser alterados em *Utilitários › Configurações* com as chaves `media_aprovacao` e `frequencia_minima`.
Alunos abaixo da média podem fazer a **recuperação especial** (no diário da disciplina): a nota substitui a média quando for maior. Os **pareceres descritivos** lançados por período aparecem no boletim.

---

## 🎨 Principais Regras Implementadas

### 📚 **Diário Eletrônico**
- ✅ **Navegação em etapas**: Turma → Disciplina → Período → Ações
- ✅ **Chamada por disciplina** e **lançamento de notas** por período
- ✅ **Bimestres configuráveis** em *Turmas › Bimestres* (com geração automática dos 4 bimestres do ano)

### 🎓 **Sistema de Enturmação**
- ✅ **Constraint de Unicidade**: Um aluno só pode estar ativo em uma turma por vez
- ✅ **Sistema de Transferência**: Confirmação prévia antes de transferir aluno
- ✅ **Preservação de Histórico**: Enturmações anteriores mantidas como registro

---

## 🏗️ Arquitetura Técnica

### **Backend**
- **Framework**: Django 5.2.6
- **Database**: SQLite (incluído no projeto com dados de demonstração)
- **Autenticação**: Django Auth, com grupos de acesso, permissões por módulo e auditoria
- **Apps**: dashboard, alunos, funcionarios, turma, diario, opcoes, aee, escola, transporte, programa, utilitarios, censo

### **Frontend**
- **CSS Framework**: Tailwind CSS 3.x (CDN) com componentes compartilhados em `templates/partials/ui_styles.html`
- **JavaScript**: Vanilla JS e Alpine.js
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
├── escola/           # Itinerários formativos e unidades curriculares
├── transporte/       # Transporte escolar
├── programa/         # Programas pedagógicos
├── utilitarios/      # Utilitários do sistema
├── censo/            # Relatórios censitários
├── templates/        # Templates HTML (generic/ e partials/ = componentes reutilizáveis)
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

### **Módulo Alunos**
- ✅ RF101-RF108: Cadastro completo de alunos
- ✅ RF201-RF209: Sistema de matrículas
- ✅ RNF101-RNF205: Todas as regras de negócio

### **Módulo Funcionários**
- ✅ RF403-RF511: Gestão de funcionários
- ✅ RNF401-RNF408: Validações e regras

### **Módulo Diário Eletrônico**
- ✅ RF701-RF705: Sistema completo de diário
- ✅ Chamada por disciplina
- ✅ Lançamento de notas e avaliações
- ✅ Relatórios e visualizações

### **Módulo Enturmação**
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
| Python | 3.10+ | Linguagem base |
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
3. Confirme que o Python 3.10+ está instalado
4. Execute `python manage.py migrate` se houver problemas com o banco

---

## 📄 Licença

Este é um projeto acadêmico desenvolvido para fins educacionais.

---

**Sistema GUTO** - Gestão Escolar Moderna e Eficiente 🚀
