# Instruções para Entrega da Atividade SonarCloud/SonarLint

## Checklist de Entrega

### 1. Configurar SonarCloud

- [ ] Acessar https://sonarcloud.io/
- [ ] Fazer login com GitHub
- [ ] Importar organização (sua conta pessoal)
- [ ] Selecionar o repositório "Guto"
- [ ] Escolher "SonarCloud Automatic Analysis" (para projetos Python)
- [ ] Aguardar primeira análise ser concluída
- [ ] Copiar o link do dashboard público

### 2. Instalar SonarLint no VS Code

- [ ] Abrir VS Code
- [ ] Pressionar `Ctrl+Shift+X` (Extensions)
- [ ] Procurar por "SonarLint"
- [ ] Clicar em "Install"
- [ ] Após instalação, configurar "Connected Mode":
  - [ ] Clicar no ícone SonarLint na barra lateral
  - [ ] Selecionar "Connect to SonarCloud"
  - [ ] Autenticar com sua conta
  - [ ] Vincular projeto local ao SonarCloud

### 3. Capturar Screenshot

- [ ] Abrir um arquivo Python do projeto (ex: `alunos/views.py`)
- [ ] Aguardar SonarLint analisar e marcar problemas
- [ ] Capturar screenshot mostrando:
  - Código com problemas sublinhados
  - Painel do SonarLint com descrição do problema
  - Nome do arquivo visível
- [ ] Salvar screenshot como `screenshot_sonarlint.png`

### 4. Completar o Questionário

- [ ] Abrir arquivo `Questionario_SonarCloud_SonarLint.md`
- [ ] Verificar se os nomes dos integrantes estão corretos no topo
- [ ] Revisar todas as respostas
- [ ] Na seção 7.1, substituir [SERÁ PREENCHIDO APÓS ANÁLISE DO SONARCLOUD] com um exemplo real do seu projeto
- [ ] Adicionar o link do dashboard do SonarCloud no final

### 5. Preparar Arquivos para Entrega

Você precisa entregar os seguintes arquivos compactados em `entregas.zip`:

1. **documento_respostas.pdf** ou **Questionario_SonarCloud_SonarLint.md**
2. **screenshot_sonarlint.png**
3. **link_sonarcloud.txt** (com o link público do dashboard)

## Como Criar o Arquivo de Entrega

### Opção 1: Manual

1. Criar uma pasta chamada `entrega_sonarcloud`
2. Copiar para dentro:
   - `Questionario_SonarCloud_SonarLint.md` (ou exportar para PDF)
   - Screenshot do SonarLint
   - Arquivo de texto com link do SonarCloud
3. Compactar a pasta como `entregas.zip`

### Opção 2: Usando script (fornecido abaixo)

Execute o script `preparar_entrega.py` que irá:
- Criar a pasta de entrega
- Copiar os arquivos necessários
- Criar o arquivo com o link do SonarCloud
- Compactar tudo automaticamente

## Link do Dashboard SonarCloud

Seu link terá o formato:
```
https://sonarcloud.io/project/overview?id=LuanCarrieiros_Guto
```

**Importante:** Configure o projeto como PÚBLICO no SonarCloud para que o professor possa acessar:
1. Vá em Project Settings
2. Clique em "Visibility"
3. Selecione "Public"

## Exemplo de Code Smell Comum em Django

Após o SonarCloud analisar seu projeto, você provavelmente encontrará:

1. **Funções muito longas** (views.py)
2. **Complexidade ciclomática alta**
3. **Strings duplicadas** (magic strings)
4. **Imports não utilizados**
5. **Variáveis não utilizadas**
6. **Falta de documentação** (docstrings)

Escolha um desses para explicar na questão 7.1.

## Dicas Finais

- **Não deixe para última hora:** A análise do SonarCloud pode levar alguns minutos
- **Verifique se o repositório está público** no GitHub e SonarCloud
- **Tire múltiplos screenshots** para ter opções
- **Revise o questionário** antes de converter para PDF
- **Teste o link do SonarCloud** em uma aba anônima para garantir que está público

## Prazos

- **Data de entrega:** 11/11/2025 até 23:59
- **Pontos:** 1 ponto
- **Tempo estimado:** 1-2 horas

## Dúvidas Comuns

**P: O SonarCloud não está analisando meu projeto**
R: Verifique se:
- O repositório é público
- A Automatic Analysis está habilitada
- Há arquivos Python no repositório
- Aguarde alguns minutos após a configuração

**P: O SonarLint não está mostrando problemas**
R: Verifique se:
- A extensão está instalada e ativada
- O arquivo tem extensão .py
- Salvou o arquivo após editar
- Reinicie o VS Code se necessário

**P: Como torno meu dashboard público?**
R: Project Settings → Visibility → Public

**P: Posso entregar em .docx ao invés de .pdf?**
R: O formato .md também é aceito, mas PDF é preferível

## Contato

Para dúvidas sobre a atividade, consulte o professor ou monitores da disciplina.

---

**Boa sorte com a atividade!**
