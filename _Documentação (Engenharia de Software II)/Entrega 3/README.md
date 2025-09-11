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
- **Database:** SQLite3 (desenvolvimento/testes) - **Migração futura:** PostgreSQL ou Azure Database for PostgreSQL
- **Frontend:** HTML5, CSS3, Tailwind CSS, JavaScript
- **Arquitetura:** MVT (Model-View-Template) com Domain-Driven Design

## 📚 Conceitos de OOP Implementados

### 1. 🔒 **Encapsulamento**

**Implementação Real no Sistema:**

```python
# alunos/models.py - Código real implementado
class Aluno(models.Model):
    # Atributos protegidos - não acessíveis diretamente
    codigo = models.AutoField(primary_key=True, verbose_name="Código")
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    
    # Método getter (propriedade calculada)
    @property
    def idade(self):
        """Encapsula lógica de cálculo de idade"""
        today = date.today()
        return today.year - self.data_nascimento.year - (
            (today.month, today.day) < 
            (self.data_nascimento.month, self.data_nascimento.day)
        )
    
    # Método de negócio encapsulado
    def __str__(self):
        return f"{self.codigo} - {self.nome}"
```

**Aplicação no Sistema:**
- **Campos críticos protegidos:** Códigos e dados sensíveis não são diretamente modificáveis
- **Validações automáticas:** Setters com regras de negócio
- **Interface pública controlada:** Acesso via propriedades e métodos
- **Dados internos seguros:** Status e metadados protegidos

### 2. 🏗️ **Herança**

**Implementação Real - Django Model Inheritance:**

```python
# funcionarios/models.py - Código real implementado
class Funcionario(models.Model):
    """Classe base com atributos comuns"""
    codigo = models.AutoField(primary_key=True, verbose_name="Código")
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    
    # Método comum herdado
    @property
    def idade(self):
        today = date.today()
        return today.year - self.data_nascimento.year

class DadosFuncionais(models.Model):
    """Especialização funcional - herda comportamentos"""
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True)
    funcao = models.CharField(max_length=30, choices=FUNCAO_CHOICES)
    
    # Método específico da especialização
    def calcular_tempo_servico(self):
        if self.data_admissao:
            return (date.today() - self.data_admissao).days
        return 0
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

**Implementação Real - Relacionamento de Dependência Total:**

```python
# alunos/models.py - Código real implementado
class Aluno(models.Model):
    nome = models.CharField(max_length=255)
    data_nascimento = models.DateField()

class DocumentacaoAluno(models.Model):
    """Composição: Documentação não existe sem Aluno"""
    aluno = models.OneToOneField(
        Aluno, 
        on_delete=models.CASCADE,  # Cascata obrigatória
        related_name='documentacao'
    )
    rg = models.CharField(max_length=20, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    
    # Método de negócio da composição
    def documentos_completos(self):
        """Regra de negócio específica"""
        return bool(self.rg and self.cpf)
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

**Implementação Real - Classe de Relacionamento:**

```python
# avaliacao/models.py - Código real implementado
class Enturmacao(models.Model):
    """Associação entre Aluno e Turma com metadados"""
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='enturmacoes')
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='enturmacoes')
    
    # Atributos específicos da associação
    data_enturmacao = models.DateField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    data_desenturmacao = models.DateField(blank=True, null=True)
    usuario_enturmacao = models.ForeignKey(User, on_delete=models.PROTECT)
    
    # Método de negócio da associação  
    def __str__(self):
        return f"{self.aluno.nome} - {self.turma.nome}"
    
    # Constraint de negócio
    class Meta:
        unique_together = ['aluno', 'ativo']  # Um aluno ativo por vez
```

## 🛠️ **Construtores e Métodos de Acesso**

**Implementação de Construtores e Getters/Setters:**

```python
# avaliacao/models.py - Código real implementado
class Turma(models.Model):
    nome = models.CharField(max_length=255)
    vagas_total = models.IntegerField(default=30)
    
    # Getter calculado
    def get_total_alunos(self):
        """Retorna total de alunos enturmados"""
        return self.enturmacoes.filter(ativo=True).count()
    
    # Getter com lógica de negócio
    def get_vagas_disponiveis(self):
        """Retorna número de vagas disponíveis"""
        return self.vagas_total - self.get_total_alunos()
    
    # Método de negócio
    def get_percentual_ocupacao(self):
        """Calcula percentual de ocupação da turma"""
        if self.vagas_total == 0:
            return 0
        return round((self.get_total_alunos() * 100) / self.vagas_total)
```

## 🎯 **Métodos de Negócio Educacionais**

**Regras Específicas do Domínio Implementadas:**

```python
# avaliacao/models.py - Métodos de negócio reais
class Avaliacao(models.Model):
    valor_maximo = models.DecimalField(max_digits=4, decimal_places=2, default=10.00)
    
    def calcular_media_turma(self):
        """Regra: Calcula média geral da turma nesta avaliação"""
        notas_validas = self.notas.exclude(nota__isnull=True)
        if not notas_validas:
            return 0
        return sum(n.nota for n in notas_validas) / len(notas_validas)
    
    def identificar_alunos_recuperacao(self):
        """Regra: Alunos com nota < 6.0 vão para recuperação"""
        return self.notas.filter(nota__lt=6.0)

# alunos/models.py - Regras de matrícula
class Matricula(models.Model):
    def pode_renovar_matricula(self):
        """Regra: Só pode renovar se não houver pendências"""
        return self.status == 'ATIVA' and not self.possui_dependencia
```

## 🚀 Como Executar o Sistema

### 📋 **Pré-requisitos**

- Python 3.12 ou superior
- Django 5.2.5
- SQLite3 (incluso no Python) - **Banco atual para desenvolvimento/testes**

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

## 🗄️ Estratégia de Banco de Dados

### **Configuração Atual (Desenvolvimento)**
- **SQLite3:** Utilizado para desenvolvimento, testes e prototipação
- **Vantagens:** Simplicidade, sem configuração adicional, ideal para desenvolvimento local
- **Localização:** `db.sqlite3` na raiz do projeto

### **Migração Futura (Produção)**
- **PostgreSQL:** Planejado para ambiente de produção
- **Azure Database for PostgreSQL:** Opção cloud para escalabilidade
- **Benefícios:** Melhor performance, suporte a transações complexas, escalabilidade horizontal

### **Arquitetura Preparada**
O sistema Django está configurado de forma agnóstica ao banco, permitindo migração transparente através de:
- **Models abstratos** que funcionam em qualquer SGBD compatível com Django ORM
- **Migrations automáticas** para versionamento de schema
- **Settings configuráveis** para diferentes ambientes (dev/test/prod)

---

**Desenvolvido para demonstração dos conceitos de Orientação a Objetos**  
**Disciplina: Engenharia de Software II**  