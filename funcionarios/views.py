from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from dashboard.models import AtividadeRecente
from .models import (
    Funcionario, DocumentacaoFuncionario, DadosFuncionais, DuploVinculo,
    Habilitacao, Escolaridade, FormacaoSuperior, Disponibilidade,
    DisciplinaFuncionario, DeficienciaFuncionario, AssociacaoProfessor, AssociacaoOutrosProfissionais
)
from .forms import (
    FuncionarioForm, DocumentacaoFuncionarioForm, DadosFuncionaisForm,
    DuploVinculoForm, HabilitacaoForm, EscolaridadeForm, FormacaoSuperiorForm,
    DisponibilidadeForm, DisciplinaFuncionarioForm, DeficienciaFuncionarioForm,
    AssociacaoProfessorForm, AssociacaoOutrosProfissionaisForm, BuscaRedeForm
)

@login_required
def funcionario_list(request):
    """
    Lista funcionários com filtros de pesquisa (RF405)
    """
    funcionarios = Funcionario.objects.all()
    
    # Filtros de pesquisa (RF405.1 e RF405.2)
    busca = request.GET.get('busca')
    tipo_busca = request.GET.get('tipo_busca', 'nome')
    arquivo_tipo = request.GET.get('arquivo_tipo', 'TODOS')
    
    if busca:
        if tipo_busca == 'codigo':
            funcionarios = funcionarios.filter(codigo__icontains=busca)
        else:  # nome
            funcionarios = funcionarios.filter(nome__icontains=busca)
    
    # Filtro por tipo de arquivo (RF405.2)
    if arquivo_tipo == 'CORRENTE':
        funcionarios = funcionarios.filter(tipo_arquivo='CORRENTE')
    elif arquivo_tipo == 'PERMANENTE':
        funcionarios = funcionarios.filter(tipo_arquivo='PERMANENTE')
    # 'TODOS' não precisa de filtro
    
    # Paginação
    paginator = Paginator(funcionarios, 25)
    page_number = request.GET.get('page')
    funcionarios_page = paginator.get_page(page_number)
    
    context = {
        'funcionarios': funcionarios_page,
        'busca': busca or '',
        'tipo_busca': tipo_busca,
        'arquivo_tipo': arquivo_tipo,
    }
    
    return render(request, 'funcionarios/funcionario_list.html', context)

@login_required
def funcionario_busca_rede(request):
    """
    RF406.1: Busca na rede por Nome, CPF ou Matrícula antes de criar
    """
    if request.method == 'POST':
        form = BuscaRedeForm(request.POST)
        if form.is_valid():
            busca = form.cleaned_data['busca']
            tipo_busca = form.cleaned_data['tipo_busca']
            
            # Simular busca na rede (implementar integração real posteriormente)
            funcionarios_encontrados = []
            
            if tipo_busca == 'nome':
                funcionarios_encontrados = Funcionario.objects.filter(nome__icontains=busca)
            elif tipo_busca == 'cpf':
                funcionarios_encontrados = Funcionario.objects.filter(documentacao__cpf=busca)
            elif tipo_busca == 'matricula':
                funcionarios_encontrados = Funcionario.objects.filter(dados_funcionais__matricula=busca)
            
            context = {
                'form': form,
                'funcionarios_encontrados': funcionarios_encontrados,
                'busca_realizada': True,
            }
            
            return render(request, 'funcionarios/funcionario_busca_rede.html', context)
    else:
        form = BuscaRedeForm()
    
    context = {
        'form': form,
        'busca_realizada': False,
    }
    
    return render(request, 'funcionarios/funcionario_busca_rede.html', context)

@login_required
def funcionario_create(request):
    """
    RF406: Cadastro de novo funcionário
    """
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                funcionario = form.save()
                
                # Registrar atividade recente
                AtividadeRecente.registrar_atividade(
                    usuario=request.user,
                    acao='CRIAR',
                    modulo='FUNCIONARIOS',
                    objeto_nome=funcionario.nome,
                    objeto_id=funcionario.codigo,
                    descricao=f'Novo funcionário cadastrado no sistema'
                )
                
                messages.success(request, 'Funcionário cadastrado com sucesso')
                return redirect('funcionarios:funcionario_edit_extended', pk=funcionario.pk)
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar funcionário: {str(e)}')
    else:
        form = FuncionarioForm()
    
    return render(request, 'funcionarios/funcionario_form.html', {
        'form': form,
        'title': 'Cadastrar Novo Funcionário',
        'is_create': True
    })

@login_required
def funcionario_edit(request, pk):
    """
    RF407: Alteração de dados do funcionário
    """
    funcionario = get_object_or_404(Funcionario, pk=pk)
    
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES, instance=funcionario)
        if form.is_valid():
            form.save()
            
            # Registrar atividade recente
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='EDITAR',
                modulo='FUNCIONARIOS',
                objeto_nome=funcionario.nome,
                objeto_id=funcionario.codigo,
                descricao=f'Dados do funcionário atualizados'
            )
            
            messages.success(request, 'Dados alterados com sucesso')
            return redirect('funcionarios:funcionario_detail', pk=funcionario.pk)
    else:
        form = FuncionarioForm(instance=funcionario)
    
    return render(request, 'funcionarios/funcionario_form.html', {
        'form': form,
        'funcionario': funcionario,
        'title': f'Editar Funcionário - {funcionario.nome}',
        'is_create': False
    })

@login_required
def funcionario_detail(request, pk):
    """
    RF408: Visualização de dados do funcionário
    """
    funcionario = get_object_or_404(Funcionario, pk=pk)
    
    context = {
        'funcionario': funcionario,
        'documentacao': getattr(funcionario, 'documentacao', None),
        'dados_funcionais': getattr(funcionario, 'dados_funcionais', None),
        'duplos_vinculos': funcionario.duplos_vinculos.all(),
        'habilitacoes': funcionario.habilitacoes.all(),
        'escolaridade': getattr(funcionario, 'escolaridade', None),
        'formacoes_superiores': funcionario.formacoes_superiores.all(),
        'disponibilidade': getattr(funcionario, 'disponibilidade', None),
        'disciplinas': funcionario.disciplinas.all(),
        'deficiencias': funcionario.deficiencias.all(),
        'associacoes': funcionario.associacoes.all(),
        'associacoes_outros': funcionario.associacoes_outros.all(),
    }
    
    return render(request, 'funcionarios/funcionario_detail.html', context)

@login_required
def funcionario_edit_extended(request, pk):
    """
    RF406.3: Cadastro estendido com abas (RNF403: salvamento automático)
    """
    funcionario = get_object_or_404(Funcionario, pk=pk)
    
    # Criar instâncias relacionadas se não existirem
    documentacao, created = DocumentacaoFuncionario.objects.get_or_create(funcionario=funcionario)
    dados_funcionais, created = DadosFuncionais.objects.get_or_create(funcionario=funcionario)
    escolaridade, created = Escolaridade.objects.get_or_create(funcionario=funcionario)
    disponibilidade, created = Disponibilidade.objects.get_or_create(funcionario=funcionario)
    
    if request.method == 'POST':
        aba_ativa = request.POST.get('aba_ativa', 'dados_pessoais')
        
        # RNF403: Salvar dados automaticamente ao navegar entre abas
        if aba_ativa == 'dados_pessoais':
            funcionario_form = FuncionarioForm(request.POST, request.FILES, instance=funcionario, prefix='func')
            if funcionario_form.is_valid():
                funcionario_form.save()
                messages.success(request, 'Dados pessoais atualizados com sucesso')
        
        elif aba_ativa == 'documentacao':
            doc_form = DocumentacaoFuncionarioForm(request.POST, instance=documentacao, prefix='doc')
            if doc_form.is_valid():
                doc_form.save()
                messages.success(request, 'Documentação atualizada com sucesso')
        
        elif aba_ativa == 'dados_funcionais':
            func_form = DadosFuncionaisForm(request.POST, instance=dados_funcionais, prefix='func_dados')
            if func_form.is_valid():
                func_form.save()
                messages.success(request, 'Dados funcionais atualizados com sucesso')
        
        elif aba_ativa == 'escolaridade':
            esc_form = EscolaridadeForm(request.POST, instance=escolaridade, prefix='esc')
            if esc_form.is_valid():
                esc_form.save()
                messages.success(request, 'Escolaridade atualizada com sucesso')
        
        elif aba_ativa == 'disponibilidade':
            disp_form = DisponibilidadeForm(request.POST, instance=disponibilidade, prefix='disp')
            if disp_form.is_valid():
                disp_form.save()
                messages.success(request, 'Disponibilidade atualizada com sucesso')
        
        return redirect('funcionarios:funcionario_edit_extended', pk=funcionario.pk)
    
    # Forms para cada aba
    funcionario_form = FuncionarioForm(instance=funcionario, prefix='func')
    doc_form = DocumentacaoFuncionarioForm(instance=documentacao, prefix='doc')
    func_dados_form = DadosFuncionaisForm(instance=dados_funcionais, prefix='func_dados')
    esc_form = EscolaridadeForm(instance=escolaridade, prefix='esc')
    disp_form = DisponibilidadeForm(instance=disponibilidade, prefix='disp')
    
    context = {
        'funcionario': funcionario,
        'funcionario_form': funcionario_form,
        'doc_form': doc_form,
        'func_dados_form': func_dados_form,
        'esc_form': esc_form,
        'disp_form': disp_form,
        'habilitacoes': funcionario.habilitacoes.all(),
        'formacoes_superiores': funcionario.formacoes_superiores.all(),
        'disciplinas': funcionario.disciplinas.all(),
        'deficiencias': funcionario.deficiencias.all(),
        'duplos_vinculos': funcionario.duplos_vinculos.all(),
    }
    
    return render(request, 'funcionarios/funcionario_extended.html', context)

@login_required
def funcionario_delete(request, pk):
    """
    RF409: Exclusão de funcionário
    """
    funcionario = get_object_or_404(Funcionario, pk=pk)
    
    # RNF407: Verificar se foi associado a uma turma
    if funcionario.associacoes.exists() or funcionario.associacoes_outros.exists():
        messages.error(request, 'Não é possível excluir um funcionário que já foi associado a uma turma. Use "Arquivo Permanente".')
        return redirect('funcionarios:funcionario_detail', pk=funcionario.pk)
    
    if request.method == 'POST':
        if request.POST.get('confirmar') == 'sim':
            nome_funcionario = funcionario.nome
            codigo_funcionario = funcionario.codigo
            
            # Registrar atividade recente antes de deletar
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='DELETAR',
                modulo='FUNCIONARIOS',
                objeto_nome=nome_funcionario,
                objeto_id=codigo_funcionario,
                descricao=f'Funcionário removido do sistema'
            )
            
            funcionario.delete()
            messages.success(request, f'Funcionário {nome_funcionario} excluído com sucesso')
            return redirect('funcionarios:funcionario_list')
    
    return render(request, 'funcionarios/funcionario_confirm_delete.html', {'funcionario': funcionario})

@login_required
def funcionario_move_to_permanent(request, pk):
    """
    RF407.1: Mover funcionário para arquivo permanente
    """
    funcionario = get_object_or_404(Funcionario, pk=pk)
    
    if request.method == 'POST':
        funcionario.tipo_arquivo = 'PERMANENTE'
        funcionario.save()
        messages.success(request, f'Funcionário {funcionario.nome} movido para o Arquivo Permanente')
        return redirect('funcionarios:funcionario_detail', pk=funcionario.pk)
    
    return render(request, 'funcionarios/funcionario_confirm_move.html', {'funcionario': funcionario})

@login_required
def funcionario_print_list(request):
    """
    RF410.1: Imprimir Lista com Código, Matrícula, Nome e CPF
    """
    funcionarios_ids = request.GET.getlist('funcionarios')
    funcionarios = Funcionario.objects.filter(id__in=funcionarios_ids)
    
    context = {
        'funcionarios': funcionarios,
        'tipo_relatorio': 'lista'
    }
    
    return render(request, 'funcionarios/funcionario_print.html', context)

@login_required
def funcionario_print_frequencia(request):
    """
    RF410.2: Imprimir Frequência mensal em branco
    """
    funcionarios_ids = request.GET.getlist('funcionarios')
    funcionarios = Funcionario.objects.filter(id__in=funcionarios_ids)
    
    context = {
        'funcionarios': funcionarios,
        'tipo_relatorio': 'frequencia'
    }
    
    return render(request, 'funcionarios/funcionario_print.html', context)

# Views para Associação de Professor (RF501-RF511)
@login_required
def associacao_professor_list(request):
    """
    RF501: Acessar associação de professores
    """
    # Filtros (RF502)
    periodo_letivo = request.GET.get('periodo_letivo')
    tipo_ensino = request.GET.get('tipo_ensino')
    serie = request.GET.get('serie')
    turno = request.GET.get('turno')
    turma = request.GET.get('turma')
    tipo_associacao = request.GET.get('tipo_associacao', 'DISCIPLINA')  # RF503
    
    associacoes = AssociacaoProfessor.objects.all()
    
    # Aplicar filtros
    if turma:
        associacoes = associacoes.filter(turma=turma)
    if tipo_associacao:
        associacoes = associacoes.filter(tipo_associacao=tipo_associacao)
    
    # RF501: Apenas docentes para associação de disciplinas
    docentes = Funcionario.objects.filter(
        dados_funcionais__funcao='DOCENTE',
        tipo_arquivo='CORRENTE'
    )
    
    context = {
        'associacoes': associacoes,
        'docentes': docentes,
        'filtros': {
            'periodo_letivo': periodo_letivo,
            'tipo_ensino': tipo_ensino,
            'serie': serie,
            'turno': turno,
            'turma': turma,
            'tipo_associacao': tipo_associacao,
        }
    }
    
    return render(request, 'funcionarios/associacao_professor_list.html', context)

@login_required
def associacao_professor_create(request):
    """
    RF505: Associar professor à disciplina
    """
    if request.method == 'POST':
        form = AssociacaoProfessorForm(request.POST)
        if form.is_valid():
            associacao = form.save(commit=False)
            associacao.usuario_cadastro = request.user
            associacao.save()
            
            messages.success(request, 'Professor associado com sucesso')
            return redirect('funcionarios:associacao_professor_list')
    else:
        form = AssociacaoProfessorForm()
    
    return render(request, 'funcionarios/associacao_professor_form.html', {
        'form': form,
        'title': 'Associar Professor'
    })

@login_required
def associacao_professor_edit(request, pk):
    """
    RF506/RF507: Gerenciar histórico e substituição de professor
    """
    associacao = get_object_or_404(AssociacaoProfessor, pk=pk)
    
    if request.method == 'POST':
        form = AssociacaoProfessorForm(request.POST, instance=associacao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Associação atualizada com sucesso')
            return redirect('funcionarios:associacao_professor_list')
    else:
        form = AssociacaoProfessorForm(instance=associacao)
    
    return render(request, 'funcionarios/associacao_professor_form.html', {
        'form': form,
        'associacao': associacao,
        'title': 'Editar Associação'
    })

@login_required
def associacao_outros_profissionais_create(request):
    """
    RF509: Associar outros profissionais (Auxiliar, Monitor, Tradutor)
    """
    if request.method == 'POST':
        form = AssociacaoOutrosProfissionaisForm(request.POST)
        if form.is_valid():
            associacao = form.save(commit=False)
            associacao.usuario_cadastro = request.user
            associacao.save()
            
            messages.success(request, 'Profissional associado com sucesso')
            return redirect('funcionarios:associacao_professor_list')
    else:
        form = AssociacaoOutrosProfissionaisForm()
    
    return render(request, 'funcionarios/associacao_outros_form.html', {
        'form': form,
        'title': 'Associar Outro Profissional'
    })

@login_required
def check_matricula_duplicada(request):
    """
    RNF405: Verificar se matrícula já está em uso
    """
    matricula = request.GET.get('matricula')
    funcionario_id = request.GET.get('funcionario_id')
    
    exists = DadosFuncionais.objects.filter(matricula=matricula)
    if funcionario_id:
        exists = exists.exclude(funcionario_id=funcionario_id)
    
    return JsonResponse({'exists': exists.exists()})

@login_required
def validate_deficiencia_multipla(request):
    """
    RNF408: Marcar automaticamente "Deficiência Múltipla"
    """
    funcionario_id = request.GET.get('funcionario_id')
    deficiencias_selecionadas = request.GET.getlist('deficiencias')
    
    if len(deficiencias_selecionadas) > 1:
        # Adicionar ou atualizar deficiência múltipla
        funcionario = get_object_or_404(Funcionario, pk=funcionario_id)
        DeficienciaFuncionario.objects.get_or_create(
            funcionario=funcionario,
            tipo_deficiencia='MULTIPLA',
            defaults={'descricao': 'Marcação automática por múltiplas deficiências'}
        )
        return JsonResponse({'multipla_marcada': True})
    
    return JsonResponse({'multipla_marcada': False})
