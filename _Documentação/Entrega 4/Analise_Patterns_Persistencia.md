# SISTEMA GUTO - ANÁLISE DE PADRÕES DA CAMADA DE PERSISTÊNCIA

**Disciplina:** Engenharia de Software II  
**Entrega:** 4 - Implementação da Camada de Persistência  
**Sistema:** GUTO - Gestão Unificada de Tecnologia Organizacional  
**Período:** 2025.2  

---

## 1. INTRODUÇÃO

O Sistema GUTO é uma aplicação Django completa para gestão escolar que implementa diversos padrões de projeto na sua camada de persistência. Este documento analisa os principais patterns utilizados, extraídos do código fonte em funcionamento e adaptados para demonstrar os conceitos solicitados.

---

## 2. PADRÕES DE PROJETO IDENTIFICADOS E IMPLEMENTADOS

### 2.1 **PATTERN: Active Record (Django ORM)**

**Localização:** `alunos/models.py`, linhas 15-45  
**Implementação no Django:**
```python
class Aluno(models.Model):
    codigo = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    data_nascimento = models.DateField()
    # ... outros campos
    
    def save(self, *args, **kwargs):
        # Lógica de negócio antes de salvar
        super().save(*args, **kwargs)
    
    def get_matriculas_ativas(self):
        return self.matricula_set.filter(status='ativa')
```

**Adaptação para demonstração:** `repository_layer.py`, linhas 55-85

**Benefícios:**
- **Simplicidade**: Cada model encapsula tanto dados quanto comportamento
- **Produtividade**: Reduz significativamente o código boilerplate
- **Integração**: Funciona nativamente com o Django Framework
- **Manutenibilidade**: Centralizavalidações e regras de negócio no modelo

---

### 2.2 **PATTERN: Repository**

**Localização demonstrativa:** `repository_layer.py`, linhas 120-220  
**Baseado em:** `alunos/views.py` - operações CRUD reais

```python
class AlunoRepository(IRepository):
    def create(self, aluno: AlunoDTO) -> int:
        # Implementação de criação
        query = """INSERT INTO alunos_aluno (nome, data_nascimento, ...) 
                   VALUES (?, ?, ...)"""
        cursor.execute(query, valores)
        return cursor.lastrowid
    
    def find_by_name(self, nome: str) -> List[AlunoDTO]:
        # Busca personalizada por nome
        query = """SELECT * FROM alunos_aluno 
                   WHERE nome LIKE ? AND tipo_arquivo = 'ativo'"""
```

**No Sistema Django Real:**
- As views utilizam `Aluno.objects.filter()`, `Aluno.objects.get()`
- QuerySets fornecem interface rica para consultas
- Managers customizados implementam lógica específica

**Benefícios:**
- **Separação de Responsabilidades**: Isola lógica de persistência
- **Testabilidade**: Permite mock dos repositórios em testes
- **Flexibilidade**: Pode trocar implementação sem afetar regras de negócio
- **Reusabilidade**: Operações podem ser reutilizadas em diferentes contextos

---

### 2.3 **PATTERN: Data Access Object (DAO)**

**Localização:** `repository_layer.py`, linhas 280-350  
**Inspirado em:** `alunos/views.py` - `MatriculaCreateView`, `encerrar_matricula`

```python
class MatriculaDAO:
    def criar_matricula(self, matricula: MatriculaDTO) -> int:
        # Validação de regra de negócio
        if self._tem_matricula_ativa(matricula.aluno_id, matricula.ano_administrativo):
            raise ValueError("Aluno já possui matrícula ativa neste ano")
        
        # Operação específica de matrícula
        query = """INSERT INTO alunos_matricula (...) VALUES (...)"""
        return cursor.lastrowid
```

**No Sistema Real:**
- Forms do Django (`MatriculaForm`) implementam validações
- Views coordenam operações complexas entre models
- Signals do Django executam ações automáticas

**Benefícios:**
- **Especialização**: Focado em operações específicas de um domínio
- **Validações Centralizadas**: Regras de negócio em local único
- **Transações**: Controle fino sobre operações atômicas
- **Performance**: Otimizações específicas para cada operação

---

### 2.4 **PATTERN: Singleton**

**Localização:** `repository_layer.py`, linhas 55-75  
**Inspirado em:** Django database connections, settings configuration

```python
class DatabaseConnection:
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect('db.sqlite3')
        return self._connection
```

**No Django Real:**
- `django.conf.settings` é um singleton global
- Connection pools são gerenciados como singletons
- Cache backends seguem padrão singleton

**Benefícios:**
- **Controle de Recursos**: Evita múltiplas conexões desnecessárias
- **Consistência**: Garante configuração única em toda aplicação
- **Performance**: Reduz overhead de criação de objetos
- **Gerenciamento**: Centraliza controle de recursos críticos

---

### 2.5 **PATTERN: Data Transfer Object (DTO)**

**Localização:** `repository_layer.py`, linhas 15-40  
**Baseado em:** Django Forms e Serializers do DRF

```python
@dataclass
class AlunoDTO:
    codigo: Optional[int] = None
    nome: str = ""
    data_nascimento: Optional[date] = None
    sexo: str = ""
    # ... outros campos
```

**No Sistema Django:**
- `ModelForms` transferem dados entre views e models
- DRF Serializers convertem entre JSON e Python objects
- `cleaned_data` dos forms funciona como DTO

**Benefícios:**
- **Desacoplamento**: Separa estrutura de dados da persistência
- **Versionamento**: Facilita mudanças na estrutura sem quebrar APIs
- **Validação**: Centraliza validação de dados de entrada
- **Serialização**: Facilita conversão entre formatos

---

### 2.6 **PATTERN: Factory**

**Localização:** `repository_layer.py`, linhas 370-385  
**Inspirado em:** Django's `apps.get_model()`, DRF ViewSets

```python
class RepositoryFactory:
    @staticmethod
    def create_aluno_repository() -> AlunoRepository:
        return AlunoRepository()
    
    @staticmethod
    def create_matricula_dao() -> MatriculaDAO:
        return MatriculaDAO()
```

**No Django Real:**
- `django.apps.get_model()` cria models dinamicamente
- `rest_framework.viewsets` factory para views
- `django.forms.modelform_factory()` cria forms

**Benefícios:**
- **Flexibilidade**: Permite trocar implementações facilmente
- **Configuração**: Centraliza criação de objetos complexos
- **Injeção de Dependência**: Facilita testes e mocks
- **Abstração**: Cliente não precisa conhecer implementação específica

---

## 3. IMPLEMENTAÇÃO NO SISTEMA GUTO REAL

### 3.1 **Arquitetura Django MVT**

O Sistema GUTO utiliza a arquitetura Model-View-Template do Django, onde:

- **Models** (`alunos/models.py`): Implementam Active Record pattern
- **Views** (`alunos/views.py`): Coordenam operações e implementam Repository-like behavior
- **Forms** (`alunos/forms.py`): Funcionam como DTOs com validação
- **Managers**: Implementam operações específicas de consulta

### 3.2 **Exemplos Reais do Código**

**Active Record em ação:**
```python
# alunos/models.py
class Aluno(models.Model):
    def get_idade(self):
        return (date.today() - self.data_nascimento).days // 365
    
    def tem_matricula_ativa(self):
        return self.matricula_set.filter(status='ativa').exists()
```

**Repository pattern via Django ORM:**
```python
# alunos/views.py
class AlunoListView(ListView):
    def get_queryset(self):
        queryset = Aluno.objects.filter(tipo_arquivo='ativo')
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(nome__icontains=busca)
        return queryset.order_by('nome')
```

---

## 4. CONCLUSÃO

O Sistema GUTO demonstra uso sofisticado de padrões de projeto na camada de persistência:

1. **Active Record** via Django ORM para operações básicas
2. **Repository** através de QuerySets e Managers customizados  
3. **DAO** implementado em Forms e Views especializadas
4. **Singleton** para configurações e conexões
5. **DTO** via Forms e Serializers
6. **Factory** para criação dinâmica de components

Esta implementação resulta em código **mantível**, **testável** e **escalável**, seguindo as melhores práticas de engenharia de software para sistemas de gestão educacional.

**Benefícios gerais alcançados:**
- Separação clara de responsabilidades
- Alta coesão e baixo acoplamento
- Facilidade de manutenção e evolução
- Reutilização de código
- Testabilidade aprimorada