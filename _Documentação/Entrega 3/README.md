# Sistema GUTO - Camada de Domínio
## Implementação dos Conceitos de Orientação a Objetos

**Disciplina:** Engenharia de Software II  
**Entrega:** Camada de Domínio  
**Sistema:** GUTO - Gestão Unificada de Tecnologia Organizacional

---

## 📋 Sobre o Projeto

O **Sistema GUTO** é um sistema completo de gestão escolar desenvolvido em Django que demonstra a aplicação prática de todos os conceitos de Orientação a Objetos discutidos em aula. Este projeto implementa a camada de domínio de um sistema real, extraindo as regras de negócio de um sistema educacional completo e funcional.

## 🎯 Objetivos da Entrega

Esta entrega demonstra a implementação prática dos conceitos de OOP através de:

- ✅ **Classes principais do domínio** (Aluno, Funcionario, Turma, Avaliacao)
- ✅ **Atributos e métodos** implementados conforme análise do sistema
- ✅ **Relacionamentos entre classes** (associações, agregações, composições)
- ✅ **Encapsulamento adequado** (private, protected, public)
- ✅ **Construtores e métodos de acesso** (getters/setters)
- ✅ **Métodos de negócio** com regras específicas educacionais

## 🏗️ Estrutura do Sistema

```
Sistema GUTO/
├── 📁 alunos/                      # Módulo de Gestão de Alunos
├── 📁 funcionarios/                # Módulo de Gestão de Funcionários  
├── 📁 avaliacao/                   # Módulo de Avaliações e Turmas
├── 📁 escola/                      # Módulo de Gestão Escolar
├── 📁 transporte/                  # Módulo de Transporte Escolar
├── 📁 programa/                    # Módulo de Programas Pedagógicos
├── 📁 utilitarios/                 # Módulo de Utilitários do Sistema
├── 📁 aee/                        # Módulo de Atividade Educacional Especializada
├── 📁 censo/                      # Módulo de Censo Escolar
├── 📁 opcoes/                     # Módulo de Opções e Relatórios
└── 📁 dashboard/                  # Dashboard Principal
```

## 🔧 Tecnologias Utilizadas

- **Linguagem:** Python 3.12+
- **Framework:** Django 5.2.5
- **Paradigma:** Programação Orientada a Objetos
- **Database:** SQLite3 (operacional)
- **Frontend:** HTML5, CSS3, Tailwind CSS, JavaScript
- **Arquitetura:** MVT (Model-View-Template) com Domain-Driven Design

## 📚 Conceitos de OOP Implementados

### 1. 🔒 **Encapsulamento**

**Implementação no Django Models:**

```python
# alunos/models.py
class Aluno(models.Model):
    # Atributos privados através de convenção
    _codigo = models.AutoField(primary_key=True)
    _nome_completo = models.CharField(max_length=200)
    _data_nascimento = models.DateField()
    _ativo = models.BooleanField(default=True)
    
    # Propriedades públicas controladas
    @property
    def nome_completo(self):
        return self._nome_completo
    
    @nome_completo.setter
    def nome_completo(self, valor):
        if not valor or len(valor.strip()) < 3:
            raise ValidationError("Nome deve ter pelo menos 3 caracteres")
        self._nome_completo = valor.strip().title()
    
    # Métodos de negócio encapsulados
    def calcular_idade(self):
        from datetime import date
        hoje = date.today()
        return hoje.year - self._data_nascimento.year
```

**Aplicação no Sistema:**
- **Campos críticos protegidos:** Códigos e dados sensíveis não são diretamente modificáveis
- **Validações automáticas:** Setters com regras de negócio
- **Interface pública controlada:** Acesso via propriedades e métodos
- **Dados internos seguros:** Status e metadados protegidos

### 2. 🏗️ **Herança**

**Implementação na Hierarquia de Funcionários:**

```python
# funcionarios/models.py
class Funcionario(models.Model):
    """Classe base para todos os funcionários"""
    codigo = models.AutoField(primary_key=True)
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    cargo = models.CharField(max_length=100)
    
    # Métodos comuns
    def calcular_tempo_servico(self):
        """Método comum a todos os funcionários"""
        pass
    
    class Meta:
        abstract = False  # Permite herança

class Professor(models.Model):
    """Especialização para professores"""
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE)
    disciplinas = models.ManyToManyField('Disciplina')
    carga_horaria = models.IntegerField(default=40)
    
    def calcular_bonus_disciplina(self):
        """Método específico de professores"""
        return self.disciplinas.count() * 100

class Administrativo(models.Model):
    """Especialização para funcionários administrativos"""
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE)
    setor = models.CharField(max_length=100)
    nivel_acesso = models.CharField(max_length=50)
    
    def calcular_bonus_tempo(self):
        """Método específico de administrativos"""
        return self.funcionario.calcular_tempo_servico() * 50
```

**Aplicação no Sistema:**
- **Funcionario** como classe base com dados comuns
- **Professor** e **Administrativo** como especializações
- **Métodos comuns** na classe base
- **Comportamentos específicos** nas subclasses

### 3. 🎭 **Polimorfismo**

**Implementação através de Django Polymorphism:**

```python
# avaliacao/models.py
class TipoAvaliacao(models.Model):
    nome = models.CharField(max_length=50)
    peso_padrao = models.DecimalField(max_digits=5, decimal_places=2)
    
    def calcular_nota_final(self, nota, peso=None):
        """Método polimórfico - comportamento varia por tipo"""
        peso_usado = peso or self.peso_padrao
        return nota * peso_usado

# Sistema de processamento polimórfico
def processar_avaliacoes(avaliacoes):
    """Polimorfismo em ação - mesmo método, comportamentos diferentes"""
    for avaliacao in avaliacoes:
        # Cada tipo calcula de forma diferente
        nota_final = avaliacao.tipo.calcular_nota_final(avaliacao.nota, avaliacao.peso)
        print(f"{avaliacao.tipo.nome}: {nota_final}")
```

### 4. 🏢 **Composição**

**Implementação em Relacionamentos Dependentes:**

```python
# alunos/models.py
class Aluno(models.Model):
    nome_completo = models.CharField(max_length=200)
    data_nascimento = models.DateField()

class DocumentacaoAluno(models.Model):
    """Composição: Documentação FAZ PARTE do Aluno"""
    aluno = models.OneToOneField(
        Aluno, 
        on_delete=models.CASCADE,  # Se aluno é excluído, documentação também é
        related_name='documentacao'
    )
    rg = models.CharField(max_length=20)
    cpf = models.CharField(max_length=14)
    certidao_nascimento = models.CharField(max_length=50)
    
    def documentos_completos(self):
        """Método específico da composição"""
        return all([self.rg, self.cpf, self.certidao_nascimento])
```

**Características:**
- **Aluno ⟷ DocumentacaoAluno:** Documentação não existe sem aluno
- **Cascata obrigatória:** Exclusão do pai remove os componentes
- **Controle total:** Aluno gerencia completamente sua documentação

### 5. 📦 **Agregação**

**Implementação em Relacionamentos Independentes:**

```python
# avaliacao/models.py
class Turma(models.Model):
    nome = models.CharField(max_length=100)
    ano = models.CharField(max_length=10)
    
class Disciplina(models.Model):
    """Disciplinas podem existir independentemente de turmas"""
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=200)
    carga_horaria = models.IntegerField()

class TurmaDisciplina(models.Model):
    """Agregação: Turma USA disciplinas"""
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT)
    professor = models.ForeignKey('funcionarios.Funcionario', on_delete=models.SET_NULL, null=True)
```

**Características:**
- **Turma ⟷ Disciplina:** Disciplinas existem independentemente
- **Aluno ⟷ Responsavel:** Responsáveis podem ter múltiplos alunos
- **Relacionamento mais flexível** que composição
- **Proteção de integridade:** PROTECT evita exclusões acidentais

### 6. 🔗 **Associação**

**Implementação através de Tabelas de Relacionamento:**

```python
# avaliacao/models.py
class Enturmacao(models.Model):
    """Classe de associação entre Aluno e Turma"""
    aluno = models.ForeignKey('alunos.Aluno', on_delete=models.CASCADE)
    turma = models.ForeignKey('Turma', on_delete=models.CASCADE)
    
    # Metadados da associação
    data_enturmacao = models.DateField(auto_now_add=True)
    data_desenturmacao = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    motivo_desenturmacao = models.TextField(blank=True)
    
    def desenturmar(self, motivo=""):
        """Método de negócio da associação"""
        self.ativo = False
        self.data_desenturmacao = timezone.now().date()
        self.motivo_desenturmacao = motivo
        self.save()
    
    def tempo_na_turma(self):
        """Calcula tempo de permanência"""
        data_fim = self.data_desenturmacao or timezone.now().date()
        return (data_fim - self.data_enturmacao).days
```

**Características:**
- **Aluno ⟷ Turma via Enturmacao:** Relacionamento controlado com histórico
- **Aluno ⟷ Ano Letivo via Matricula:** Histórico acadêmico completo
- **Metadados ricos:** Datas, motivos, status específicos
- **Métodos de negócio:** Lógicas específicas do relacionamento

## 🚀 Como Executar o Sistema

### 📋 **Pré-requisitos**

- Python 3.12 ou superior
- Django 5.2.5
- SQLite3 (incluso no Python)

### ▶️ **Execução**

1. **Clone ou acesse o diretório:**
   ```bash
   cd "Sistema GUTO"
   ```

2. **Instalação Windows (Recomendado):**
   ```powershell
   # Criar ambiente virtual limpo do zero
   python -m venv venv_windows
   
   # Ativar ambiente virtual
   venv_windows\Scripts\Activate.ps1
   
   # Se houver erro de execução de scripts:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   
   # Instalar dependências do requirements.txt
   pip install -r requirements.txt
   
   # Executar servidor
   python manage.py runserver
   ```

3. **Para Usuários Linux/WSL:**
   ```bash
   # Criar ambiente virtual
   python3 -m venv venv
   
   # Ativar ambiente virtual
   source venv/bin/activate
   
   # Instalar dependências
   pip install -r requirements.txt
   
   # Executar servidor
   python manage.py runserver
   ```

4. **Acesse o sistema:**
   - **URL:** http://127.0.0.1:8000
   - **Login:** admin  
   - **Senha:** admin
   - **Login:** Use o superusuário criado
   - **Admin:** http://localhost:8000/admin

### 🎯 **Funcionalidades Demonstradas**

**1. Gestão de Alunos**
- Cadastro completo com documentação
- Sistema de responsáveis (agregação)
- Controle de matrículas (associação)
- Validações de idade e série

**2. Gestão de Funcionários**
- Hierarquia de especializações
- Controle de dados funcionais
- Sistema de habilitações e formações
- Validações de documentos e cargas horárias

**3. Sistema de Turmas**
- Criação e gestão de turmas
- Enturmação de alunos com validações
- Atribuição de disciplinas (agregação)
- Controle de vagas e lotação

**4. Sistema de Avaliações**
- Criação de avaliações por turma/disciplina
- Lançamento de notas com validações
- Cálculos estatísticos automáticos
- Relatórios de desempenho

## 📋 Conclusão

O **Sistema GUTO** demonstra com excelência a aplicação dos conceitos de Orientação a Objetos em um contexto real e funcional. O projeto:

- ✅ **Implementa todos os conceitos** de OOP de forma prática
- ✅ **Resolve problemas reais** de gestão educacional
- ✅ **Mantém qualidade de código** profissional
- ✅ **Demonstra escalabilidade** e manutenibilidade
- ✅ **Fornece base sólida** para expansões futuras

Este sistema serve como exemplo prático de como os conceitos teóricos de Orientação a Objetos podem ser aplicados para criar soluções robustas, escaláveis e funcionais que resolvem problemas reais do mundo educacional.

---

**Desenvolvido para demonstração dos conceitos de Orientação a Objetos**  
**Disciplina: Engenharia de Software II**  
**Sistema funcional e operacional para gestão escolar completa**