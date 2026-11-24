import calendar
from datetime import date

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from dashboard.models import AtividadeRecente
from .models import (
    Funcionario, DocumentacaoFuncionario, DadosFuncionais, Escolaridade,
    Disponibilidade, DeficienciaFuncionario, AssociacaoProfessor, AssociacaoOutrosProfissionais
)
from .forms import (
    FuncionarioForm, DocumentacaoFuncionarioForm, DadosFuncionaisForm,
    EscolaridadeForm, HabilitacaoForm, DisciplinaFuncionarioForm, DeficienciaFuncionarioForm, DisponibilidadeForm, AssociacaoProfessorForm, AssociacaoOutrosProfissionaisForm,
    BuscaRedeForm
)

@login_required
def funcionarios_home(request):
    """
    Página inicial do módulo de Funcionários com estatísticas e ações rápidas
    """
    # Estatísticas gerais
    total_funcionarios = Funcionario.objects.count()
    funcionarios_ativos = Funcionario.objects.filter(tipo_arquivo='CORRENTE').count()

    # Contagem por função
    total_professores = DadosFuncionais.objects.filter(funcao='DOCENTE').count()
    total_administrativos = DadosFuncionais.objects.exclude(funcao='DOCENTE').count()

    # Últimos 5 funcionários cadastrados
    funcionarios_recentes = Funcionario.objects.all().order_by('-codigo')[:5]

    # Distribuição por função
    funcionarios_por_funcao = []
    funcoes = DadosFuncionais.objects.values('funcao').annotate(total=Count('funcao'))
    for funcao in funcoes:
        percentual = (funcao['total'] / total_funcionarios * 100) if total_funcionarios > 0 else 0
        funcionarios_por_funcao.append({
            'nome': dict(DadosFuncionais.FUNCAO_CHOICES).get(funcao['funcao'], funcao['funcao']),
            'total': funcao['total'],
            'percentual': percentual
        })

    context = {
        'total_funcionarios': total_funcionarios,
        'total_professores': total_professores,
        'total_administrativos': total_administrativos,
        'funcionarios_ativos': funcionarios_ativos,
        'funcionarios_recentes': funcionarios_recentes,
        'funcionarios_por_funcao': funcionarios_por_funcao,
    }

    return render(request, 'funcionarios/funcionarios_home.html', context)

@login_required
def funcionario_list(request):
    """
    Lista funcionários com filtros de pesquisa (RF405)
    """
    funcionarios = Funcionario.objects.select_related('dados_funcionais').all()
    
    # Filtros de pesquisa
    search = request.GET.get('search', '')
    cargo = request.GET.get('cargo', '')
    ativo = request.GET.get('ativo', '')
    
    # Aplicar filtros
    if search:
        funcionarios = funcionarios.filter(
            Q(nome__icontains=search) | 
            Q(codigo__icontains=search) | 
            Q(dados_funcionais__matricula__icontains=search)
        )
    
    if cargo:
        funcionarios = funcionarios.filter(dados_funcionais__funcao=cargo)
    
    if ativo:
        if ativo == 'True':
            # Mostrar apenas funcionários ativos (arquivo corrente)
            funcionarios = funcionarios.filter(tipo_arquivo='CORRENTE')
        else:
            # Mostrar apenas funcionários inativos (arquivo permanente)
            funcionarios = funcionarios.filter(tipo_arquivo='PERMANENTE')
    
    # Ordenar por nome
    funcionarios = funcionarios.order_by('nome')
    
    # Paginação
    paginator = Paginator(funcionarios, 25)
    page_number = request.GET.get('page')
    funcionarios_page = paginator.get_page(page_number)
    
    context = {
        'funcionarios': funcionarios_page,
        'funcoes': DadosFuncionais.FUNCAO_CHOICES,
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
            
            funcionarios_encontrados = Funcionario.objects.none()
            
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
                funcionario = form.save(user=request.user)
                
                # Registrar atividade recente
                AtividadeRecente.registrar_atividade(
                    usuario=request.user,
                    acao='CRIAR',
                    modulo='FUNCIONARIOS',
                    objeto_nome=funcionario.nome,
                    objeto_id=funcionario.codigo,
                    descricao='Novo funcionário cadastrado no sistema'
                )
                
                messages.success(request, 'Funcionário cadastrado com sucesso')
                return redirect('funcionarios:funcionario_list')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar funcionário: {str(e)}')
        else:
            # Exibir erros de validação para o usuário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
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
                descricao='Dados do funcionário atualizados'
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
    
    # Obter instâncias relacionadas se existirem
    try:
        documentacao = DocumentacaoFuncionario.objects.get(funcionario=funcionario)
    except DocumentacaoFuncionario.DoesNotExist:
        documentacao = None
    
    try:
        dados_funcionais = DadosFuncionais.objects.get(funcionario=funcionario)
    except DadosFuncionais.DoesNotExist:
        dados_funcionais = None
    
    try:
        escolaridade = Escolaridade.objects.get(funcionario=funcionario)
    except Escolaridade.DoesNotExist:
        escolaridade = None
    
    try:
        disponibilidade = Disponibilidade.objects.get(funcionario=funcionario)
    except Disponibilidade.DoesNotExist:
        disponibilidade = None
    
    # Abas com listas (habilitações, disciplinas e deficiências): inclusão e remoção
    listas = {
        'habilitacao': (HabilitacaoForm, funcionario.habilitacoes, 'Habilitação'),
        'disciplinas': (DisciplinaFuncionarioForm, funcionario.disciplinas, 'Disciplina'),
        'deficiencias': (DeficienciaFuncionarioForm, funcionario.deficiencias, 'Deficiência'),
    }
    if request.method == 'POST' and request.POST.get('aba_ativa') in listas:
        aba = request.POST['aba_ativa']
        form_class, relacionados, rotulo = listas[aba]
        remover_id = request.POST.get('remover_id')
        if remover_id:
            relacionados.filter(pk=remover_id).delete()
            messages.success(request, f'{rotulo} removida.')
        else:
            form = form_class(request.POST, prefix=aba)
            if form.is_valid():
                item = form.save(commit=False)
                item.funcionario = funcionario
                item.save()
                messages.success(request, f'{rotulo} adicionada com sucesso.')
                # RNF408: mais de uma deficiência marca automaticamente "Deficiência Múltipla"
                if aba == 'deficiencias' and funcionario.deficiencias.exclude(tipo_deficiencia='MULTIPLA').count() > 1:
                    DeficienciaFuncionario.objects.get_or_create(
                        funcionario=funcionario, tipo_deficiencia='MULTIPLA',
                        defaults={'descricao': 'Marcação automática por múltiplas deficiências'},
                    )
            else:
                for erros in form.errors.values():
                    for erro in erros:
                        messages.error(request, erro)
        return redirect(f"{reverse('funcionarios:funcionario_edit_extended', args=[funcionario.pk])}?aba={aba}")

    if request.method == 'POST':
        aba_ativa = request.POST.get('aba_ativa', 'dados_pessoais')

        # RNF403: Salvar dados automaticamente ao navegar entre abas
        if aba_ativa == 'dados_pessoais':
            funcionario_form = FuncionarioForm(request.POST, request.FILES, instance=funcionario)
            if funcionario_form.is_valid():
                funcionario_form.save(user=request.user)
                messages.success(request, 'Dados pessoais atualizados com sucesso')
            else:
                # Mostrar erros de validação
                for field, errors in funcionario_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        elif aba_ativa == 'documentacao':
            doc_form = DocumentacaoFuncionarioForm(request.POST, instance=documentacao)
            if doc_form.is_valid():
                doc_instance = doc_form.save(commit=False)
                doc_instance.funcionario = funcionario
                doc_instance.save()
                messages.success(request, 'Documentação atualizada com sucesso')
            else:
                for field, errors in doc_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        elif aba_ativa == 'dados_funcionais':
            func_form = DadosFuncionaisForm(request.POST, instance=dados_funcionais)
            if func_form.is_valid():
                func_instance = func_form.save(commit=False)
                func_instance.funcionario = funcionario
                func_instance.save()
                messages.success(request, 'Dados funcionais atualizados com sucesso')
            else:
                for field, errors in func_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        elif aba_ativa == 'escolaridade':
            esc_form = EscolaridadeForm(request.POST, instance=escolaridade)
            if esc_form.is_valid():
                esc_instance = esc_form.save(commit=False)
                esc_instance.funcionario = funcionario
                esc_instance.save()
                messages.success(request, 'Escolaridade atualizada com sucesso')
            else:
                for field, errors in esc_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        elif aba_ativa == 'disponibilidade':
            disp_form = DisponibilidadeForm(request.POST, instance=disponibilidade)
            if disp_form.is_valid():
                disp_instance = disp_form.save(commit=False)
                disp_instance.funcionario = funcionario
                disp_instance.save()
                messages.success(request, 'Disponibilidade atualizada com sucesso')
            else:
                for field, errors in disp_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        aba_destino = {
            'dados_pessoais': 'pessoais', 'dados_funcionais': 'funcionais',
        }.get(aba_ativa, aba_ativa)
        return redirect(f"{reverse('funcionarios:funcionario_edit_extended', args=[funcionario.pk])}?aba={aba_destino}")

    # Forms para cada aba
    funcionario_form = FuncionarioForm(instance=funcionario)
    doc_form = DocumentacaoFuncionarioForm(instance=documentacao)
    func_dados_form = DadosFuncionaisForm(instance=dados_funcionais)
    esc_form = EscolaridadeForm(instance=escolaridade)
    disp_form = DisponibilidadeForm(instance=disponibilidade)
    
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
        'habilitacao_form': HabilitacaoForm(prefix='habilitacao'),
        'disciplina_form': DisciplinaFuncionarioForm(prefix='disciplinas'),
        'deficiencia_form': DeficienciaFuncionarioForm(prefix='deficiencias'),
        'aba_inicial': request.GET.get('aba') if request.GET.get('aba') in (
            'pessoais', 'documentacao', 'funcionais', 'habilitacao', 'escolaridade',
            'disponibilidade', 'disciplinas', 'deficiencias') else 'pessoais',
    }

    return render(request, 'funcionarios/funcionario_edit_extended.html', context)

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
        action = request.POST.get('action')
        confirmacao = request.POST.get('confirmacao', '').strip()
        
        # Verificar se o nome foi digitado corretamente
        if confirmacao == funcionario.nome and action:
            nome_funcionario = funcionario.nome
            codigo_funcionario = funcionario.codigo
            
            if action == 'archive':
                # Mover para arquivo permanente
                funcionario.tipo_arquivo = 'PERMANENTE'
                funcionario.save()
                
                # Registrar atividade recente
                AtividadeRecente.registrar_atividade(
                    usuario=request.user,
                    acao='EDITAR',
                    modulo='FUNCIONARIOS',
                    objeto_nome=nome_funcionario,
                    objeto_id=codigo_funcionario,
                    descricao='Funcionário movido para arquivo permanente'
                )
                
                messages.success(request, f'Funcionário {nome_funcionario} movido para arquivo permanente')
                return redirect('funcionarios:funcionario_list')
                
            elif action == 'delete':
                # Excluir permanentemente
                # Registrar atividade recente antes de deletar
                AtividadeRecente.registrar_atividade(
                    usuario=request.user,
                    acao='DELETAR',
                    modulo='FUNCIONARIOS',
                    objeto_nome=nome_funcionario,
                    objeto_id=codigo_funcionario,
                    descricao='Funcionário removido permanentemente do sistema'
                )
                
                funcionario.delete()
                messages.success(request, f'Funcionário {nome_funcionario} excluído permanentemente')
                return redirect('funcionarios:funcionario_list')
        else:
            messages.error(request, 'Nome de confirmação incorreto ou ação não selecionada')
    
    return render(request, 'funcionarios/funcionario_confirm_delete.html', {'funcionario': funcionario})

@login_required
def funcionario_move_to_permanent(request, pk):
    """
    RF407.1: Mover funcionário para o arquivo permanente (ou de volta ao corrente)
    """
    funcionario = get_object_or_404(Funcionario, pk=pk)
    destino = 'CORRENTE' if funcionario.tipo_arquivo == 'PERMANENTE' else 'PERMANENTE'

    if request.method == 'POST':
        funcionario.tipo_arquivo = destino
        funcionario.save(update_fields=['tipo_arquivo'])
        AtividadeRecente.registrar_atividade(
            usuario=request.user, acao='EDITAR', modulo='FUNCIONARIOS',
            objeto_nome=funcionario.nome, objeto_id=funcionario.pk,
            descricao=f'Movido para o arquivo {destino.lower()}',
        )
        messages.success(request, f'Funcionário {funcionario.nome} movido para o Arquivo {destino.capitalize()}.')
        return redirect('funcionarios:funcionario_detail', pk=funcionario.pk)

    return render(request, 'funcionarios/funcionario_confirm_move.html', {
        'funcionario': funcionario, 'destino': destino,
    })


@login_required
def funcionario_print(request):
    """
    RF410: Impressão da lista de funcionários (RF410.1) ou da folha de frequência mensal em branco (RF410.2).
    Usa os mesmos filtros da lista de funcionários.
    """
    funcionarios = Funcionario.objects.select_related('dados_funcionais', 'documentacao').order_by('nome')
    cargo = request.GET.get('cargo', '')
    ativo = request.GET.get('ativo', '')
    search = request.GET.get('search', '')
    if search:
        funcionarios = funcionarios.filter(
            Q(nome__icontains=search) | Q(codigo__icontains=search) | Q(dados_funcionais__matricula__icontains=search)
        )
    if cargo:
        funcionarios = funcionarios.filter(dados_funcionais__funcao=cargo)
    if ativo == 'True':
        funcionarios = funcionarios.filter(tipo_arquivo='CORRENTE')
    elif ativo == 'False':
        funcionarios = funcionarios.filter(tipo_arquivo='PERMANENTE')

    tipo = 'frequencia' if request.GET.get('tipo') == 'frequencia' else 'lista'
    hoje = date.today()
    dias_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    context = {
        'funcionarios': funcionarios,
        'tipo_relatorio': tipo,
        'dias': range(1, dias_mes + 1),
        'mes_referencia': hoje,
    }
    return render(request, 'funcionarios/funcionario_print.html', context)


# Views para Associação de Professor (RF501-RF511)
@login_required
def associacao_professor_list(request):
    """
    RF501-RF503: Associações de professores e outros profissionais às turmas
    """
    turma = request.GET.get('turma', '')
    tipo_associacao = request.GET.get('tipo_associacao', '')
    vigentes = request.GET.get('vigentes', '1')

    associacoes = AssociacaoProfessor.objects.select_related('funcionario').order_by('turma', 'disciplina')
    outros = AssociacaoOutrosProfissionais.objects.select_related('funcionario').order_by('turma')
    if turma:
        associacoes = associacoes.filter(turma=turma)
        outros = outros.filter(turma=turma)
    if tipo_associacao:
        associacoes = associacoes.filter(tipo_associacao=tipo_associacao)
    if vigentes == '1':
        hoje = date.today()
        associacoes = associacoes.filter(Q(data_termino__isnull=True) | Q(data_termino__gte=hoje))
        outros = outros.filter(Q(data_termino__isnull=True) | Q(data_termino__gte=hoje))

    context = {
        'associacoes': associacoes,
        'outros': outros,
        'turmas': sorted(set(AssociacaoProfessor.objects.values_list('turma', flat=True))
                         | set(AssociacaoOutrosProfissionais.objects.values_list('turma', flat=True))),
        'tipos': AssociacaoProfessor.TIPO_ASSOCIACAO_CHOICES,
        'filtros': {'turma': turma, 'tipo_associacao': tipo_associacao, 'vigentes': vigentes},
    }
    return render(request, 'funcionarios/associacao_professor_list.html', context)


def _form_associacao(request, form, title, icon):
    return render(request, 'generic/form.html', {
        'form': form, 'title': title, 'icon': icon,
        'cancel_url': reverse('funcionarios:associacao_professor_list'),
    })


@login_required
def associacao_professor_create(request):
    """
    RF505: Associar professor à disciplina/turma
    """
    form = AssociacaoProfessorForm(request.POST or None, initial={'data_inicio': date.today()})
    if request.method == 'POST' and form.is_valid():
        associacao = form.save(commit=False)
        associacao.usuario_cadastro = request.user
        associacao.save()
        messages.success(request, 'Professor associado com sucesso.')
        return redirect('funcionarios:associacao_professor_list')
    return _form_associacao(request, form, 'Associar Professor', 'fa-chalkboard-teacher')


@login_required
def associacao_professor_edit(request, pk):
    """
    RF506/RF507: Gerenciar histórico e substituição de professor
    """
    associacao = get_object_or_404(AssociacaoProfessor, pk=pk)
    form = AssociacaoProfessorForm(request.POST or None, instance=associacao)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Associação atualizada com sucesso.')
        return redirect('funcionarios:associacao_professor_list')
    return _form_associacao(request, form, 'Editar Associação de Professor', 'fa-chalkboard-teacher')


@login_required
def associacao_outros_profissionais_create(request):
    """
    RF509: Associar outros profissionais (Auxiliar, Monitor, Tradutor)
    """
    form = AssociacaoOutrosProfissionaisForm(request.POST or None, initial={'data_inicio': date.today()})
    if request.method == 'POST' and form.is_valid():
        associacao = form.save(commit=False)
        associacao.usuario_cadastro = request.user
        associacao.save()
        messages.success(request, 'Profissional associado com sucesso.')
        return redirect('funcionarios:associacao_professor_list')
    return _form_associacao(request, form, 'Associar Outro Profissional', 'fa-user-friends')
