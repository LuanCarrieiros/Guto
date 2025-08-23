from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from dashboard.models import AtividadeRecente
from .models import Aluno, DocumentacaoAluno, Responsavel, TransporteAluno, Matricula
from .forms import AlunoForm, DocumentacaoAlunoForm, ResponsavelForm, TransporteAlunoForm, MatriculaForm

@login_required
def aluno_list(request):
    """
    Lista todos os alunos com filtros de pesquisa (RF103)
    """
    alunos = Aluno.objects.all()
    
    # Filtros de pesquisa (RF103.1 e RF103.2)
    busca = request.GET.get('busca')
    tipo_busca = request.GET.get('tipo_busca', 'nome')
    arquivo_tipo = request.GET.get('arquivo_tipo', 'TODOS')
    aluno_gemeo = request.GET.get('aluno_gemeo', False)
    
    if busca:
        if tipo_busca == 'codigo':
            alunos = alunos.filter(codigo__icontains=busca)
        else:  # nome
            alunos = alunos.filter(nome__icontains=busca)
    
    # Filtro por tipo de arquivo
    if arquivo_tipo == 'CORRENTE':
        alunos = alunos.filter(tipo_arquivo='CORRENTE')
    elif arquivo_tipo == 'PERMANENTE':
        alunos = alunos.filter(tipo_arquivo='PERMANENTE')
    # 'TODOS' não precisa de filtro
    
    # Filtro para alunos gêmeos
    if aluno_gemeo:
        alunos = alunos.filter(aluno_gemeo=True)
    
    # Estatísticas para os cards
    total_alunos = Aluno.objects.count()
    alunos_corrente = Aluno.objects.filter(tipo_arquivo='CORRENTE').count()
    alunos_permanente = Aluno.objects.filter(tipo_arquivo='PERMANENTE').count()
    alunos_gemeos = Aluno.objects.filter(aluno_gemeo=True).count()
    
    # Paginação
    paginator = Paginator(alunos, 25)
    page_number = request.GET.get('page')
    alunos_page = paginator.get_page(page_number)
    
    context = {
        'alunos': alunos_page,
        'busca': busca or '',
        'tipo_busca': tipo_busca,
        'arquivo_tipo': arquivo_tipo,
        'aluno_gemeo': aluno_gemeo,
        'total_alunos': total_alunos,
        'alunos_corrente': alunos_corrente,
        'alunos_permanente': alunos_permanente,
        'alunos_gemeos': alunos_gemeos,
    }
    
    return render(request, 'alunos/aluno_list.html', context)

@login_required
def aluno_create(request):
    """
    Cadastro básico de aluno (RF104)
    """
    if request.method == 'POST':
        form = AlunoForm(request.POST, request.FILES)
        if form.is_valid():
            aluno = form.save(commit=False)
            aluno.usuario_cadastro = request.user
            aluno.save()
            
            # Registrar atividade recente
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='CRIAR',
                modulo='ALUNOS',
                objeto_nome=aluno.nome,
                objeto_id=aluno.codigo,
                descricao=f'Novo aluno cadastrado no sistema'
            )
            
            messages.success(request, 'Inclusão do Aluno realizada com sucesso.')
            
            # RF110: Redirecionar com flag para mostrar pop-up
            return redirect('alunos:aluno_list')
    else:
        form = AlunoForm()
    
    return render(request, 'alunos/aluno_form.html', {
        'form': form,
        'title': 'Cadastrar Novo Aluno',
        'is_create': True
    })

@login_required
def aluno_edit(request, pk):
    """
    Edição de dados básicos do aluno (RF106)
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    
    if request.method == 'POST':
        form = AlunoForm(request.POST, request.FILES, instance=aluno)
        if form.is_valid():
            form.save()
            
            # Registrar atividade recente
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='EDITAR',
                modulo='ALUNOS',
                objeto_nome=aluno.nome,
                objeto_id=aluno.codigo,
                descricao=f'Dados básicos do aluno atualizados'
            )
            
            messages.success(request, 'Alteração do Aluno realizada com sucesso')
            return redirect('alunos:aluno_detail', pk=aluno.pk)
    else:
        form = AlunoForm(instance=aluno)
    
    return render(request, 'alunos/aluno_form.html', {
        'form': form,
        'aluno': aluno,
        'title': f'Editar Aluno - {aluno.nome}',
        'is_create': False
    })

@login_required
def aluno_detail(request, pk):
    """
    Visualização detalhada do aluno (RF106 - Consultar)
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    
    # Registrar atividade recente de visualização
    AtividadeRecente.registrar_atividade(
        usuario=request.user,
        acao='VISUALIZAR',
        modulo='ALUNOS',
        objeto_nome=aluno.nome,
        objeto_id=aluno.codigo,
        descricao=f'Visualizou detalhes do aluno'
    )
    
    context = {
        'aluno': aluno,
        'documentacao': getattr(aluno, 'documentacao', None),
        'responsaveis': aluno.responsaveis.all(),
        'transporte': getattr(aluno, 'transporte', None),
        'matriculas': aluno.matriculas.all().order_by('-ano_administrativo'),
    }
    
    return render(request, 'alunos/aluno_detail.html', context)

@login_required
def aluno_edit_extended(request, pk):
    """
    Cadastro estendido do aluno com abas (RF105)
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    
    # Criar instâncias relacionadas se não existirem
    documentacao, created = DocumentacaoAluno.objects.get_or_create(aluno=aluno)
    transporte, created = TransporteAluno.objects.get_or_create(aluno=aluno)
    
    if request.method == 'POST':
        aba_ativa = request.POST.get('aba_ativa', 'identificacao')
        
        if aba_ativa == 'identificacao':
            aluno_form = AlunoForm(request.POST, request.FILES, instance=aluno, prefix='aluno')
            if aluno_form.is_valid():
                aluno_form.save()
                messages.success(request, 'Dados de identificação atualizados com sucesso')
        
        elif aba_ativa == 'documentacao':
            doc_form = DocumentacaoAlunoForm(request.POST, instance=documentacao, prefix='doc')
            if doc_form.is_valid():
                doc_form.save()
                messages.success(request, 'Documentação atualizada com sucesso')
        
        elif aba_ativa == 'transporte':
            trans_form = TransporteAlunoForm(request.POST, instance=transporte, prefix='trans')
            if trans_form.is_valid():
                trans_form.save()
                messages.success(request, 'Dados de transporte atualizados com sucesso')
        
        return redirect('alunos:aluno_edit_extended', pk=aluno.pk)
    
    # Forms para cada aba
    aluno_form = AlunoForm(instance=aluno, prefix='aluno')
    doc_form = DocumentacaoAlunoForm(instance=documentacao, prefix='doc')
    trans_form = TransporteAlunoForm(instance=transporte, prefix='trans')
    
    context = {
        'aluno': aluno,
        'aluno_form': aluno_form,
        'doc_form': doc_form,
        'trans_form': trans_form,
        'responsaveis': aluno.responsaveis.all(),
    }
    
    return render(request, 'alunos/aluno_extended.html', context)

@login_required
def aluno_delete(request, pk):
    """
    Exclusão de aluno (RF107)
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    
    # RNF106: Verificar vínculos antes de excluir
    if aluno.matriculas.exists():
        messages.error(request, 'Não é possível excluir um aluno que possui matrículas no sistema.')
        return redirect('alunos:aluno_detail', pk=aluno.pk)
    
    if request.method == 'POST':
        if request.POST.get('confirmar') == 'sim':
            nome_aluno = aluno.nome
            codigo_aluno = aluno.codigo
            
            # Registrar atividade recente antes de deletar
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='DELETAR',
                modulo='ALUNOS',
                objeto_nome=nome_aluno,
                objeto_id=codigo_aluno,
                descricao=f'Aluno removido do sistema'
            )
            
            aluno.delete()
            messages.success(request, f'Aluno {nome_aluno} excluído com sucesso')
            return redirect('alunos:aluno_list')
    
    return render(request, 'alunos/aluno_confirm_delete.html', {'aluno': aluno})

@login_required
def aluno_move_to_permanent(request, pk):
    """
    Mover aluno para arquivo permanente (RF106.1)
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    
    if request.method == 'POST':
        aluno.tipo_arquivo = 'PERMANENTE'
        aluno.save()
        messages.success(request, f'Aluno {aluno.nome} movido para o Arquivo Permanente')
        return redirect('alunos:aluno_detail', pk=aluno.pk)
    
    return render(request, 'alunos/aluno_confirm_move.html', {'aluno': aluno})

@login_required
def aluno_print(request, pk):
    """
    Impressão dos dados do aluno (RF108)
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    
    context = {
        'aluno': aluno,
        'documentacao': getattr(aluno, 'documentacao', None),
        'responsaveis': aluno.responsaveis.all(),
        'transporte': getattr(aluno, 'transporte', None),
        'matriculas': aluno.matriculas.all().order_by('-ano_administrativo'),
    }
    
    return render(request, 'alunos/aluno_print.html', context)

# Views para Matrículas
@login_required
def matricula_create(request, aluno_pk):
    """
    Criar nova matrícula para um aluno (RF204)
    """
    aluno = get_object_or_404(Aluno, pk=aluno_pk)
    
    if request.method == 'POST':
        form = MatriculaForm(request.POST)
        if form.is_valid():
            matricula = form.save(commit=False)
            matricula.aluno = aluno
            matricula.usuario_cadastro = request.user
            matricula.save()
            
            messages.success(request, 'Matrícula efetuada com sucesso')
            return redirect('alunos:aluno_detail', pk=aluno.pk)
    else:
        form = MatriculaForm()
    
    return render(request, 'alunos/matricula_form.html', {
        'form': form,
        'aluno': aluno,
        'title': f'Nova Matrícula - {aluno.nome}'
    })

@login_required
def matricula_edit(request, pk):
    """
    Editar matrícula (RF205)
    """
    matricula = get_object_or_404(Matricula, pk=pk)
    
    # RNF202: Não permitir alteração de matrícula encerrada
    if matricula.status == 'ENCERRADA':
        messages.error(request, 'Não é possível alterar uma matrícula que já foi encerrada.')
        return redirect('alunos:aluno_detail', pk=matricula.aluno.pk)
    
    if request.method == 'POST':
        form = MatriculaForm(request.POST, instance=matricula)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matrícula alterada com sucesso')
            return redirect('alunos:aluno_detail', pk=matricula.aluno.pk)
    else:
        form = MatriculaForm(instance=matricula)
    
    return render(request, 'alunos/matricula_form.html', {
        'form': form,
        'matricula': matricula,
        'aluno': matricula.aluno,
        'title': f'Editar Matrícula - {matricula.aluno.nome}'
    })

@login_required
def matricula_delete(request, pk):
    """
    Excluir matrícula (RF206)
    """
    matricula = get_object_or_404(Matricula, pk=pk)
    
    # RNF203: Verificar se pode excluir
    if matricula.status == 'ENCERRADA':
        messages.error(request, 'Não é possível excluir matrículas encerradas. A matrícula deve ser encerrada.')
        return redirect('alunos:aluno_detail', pk=matricula.aluno.pk)
    
    if request.method == 'POST':
        if request.POST.get('confirmar') == 'sim':
            aluno = matricula.aluno
            matricula.delete()
            messages.success(request, 'Exclusão realizada com sucesso')
            return redirect('alunos:aluno_detail', pk=aluno.pk)
    
    return render(request, 'alunos/matricula_confirm_delete.html', {'matricula': matricula})

@login_required
def matricula_encerrar(request, pk):
    """
    Encerrar matrícula (RF207)
    """
    matricula = get_object_or_404(Matricula, pk=pk)
    
    if request.method == 'POST':
        data_encerramento = request.POST.get('data_encerramento')
        motivo_encerramento = request.POST.get('motivo_encerramento')
        
        if data_encerramento and motivo_encerramento:
            matricula.status = 'ENCERRADA'
            matricula.data_encerramento = data_encerramento
            matricula.motivo_encerramento = motivo_encerramento
            matricula.save()
            
            messages.success(request, 'Matrícula encerrada com sucesso')
            return redirect('alunos:aluno_detail', pk=matricula.aluno.pk)
        else:
            messages.error(request, 'Data e motivo do encerramento são obrigatórios')
    
    return render(request, 'alunos/matricula_encerrar.html', {'matricula': matricula})

@login_required
def matricula_reativar(request, pk):
    """
    Reativar matrícula (RF208)
    """
    matricula = get_object_or_404(Matricula, pk=pk)
    
    # RNF204: Verificar se pode reativar
    if matricula.aluno.tipo_arquivo == 'PERMANENTE':
        messages.error(request, 'Não é possível reativar matrícula de aluno no Arquivo Permanente')
        return redirect('alunos:aluno_detail', pk=matricula.aluno.pk)
    
    if request.method == 'POST':
        matricula.status = 'ATIVA'
        matricula.data_encerramento = None
        matricula.motivo_encerramento = None
        matricula.save()
        
        messages.success(request, 'Matrícula reativada com sucesso')
        return redirect('alunos:aluno_detail', pk=matricula.aluno.pk)
    
    return render(request, 'alunos/matricula_reativar.html', {'matricula': matricula})
