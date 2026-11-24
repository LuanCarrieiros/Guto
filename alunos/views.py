from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from dashboard.models import AtividadeRecente
from .models import Aluno, DocumentacaoAluno, Responsavel, TransporteAluno, Matricula
from utilitarios.forms import DadosAdicionaisAlunoForm
from .forms import AlunoForm, DocumentacaoAlunoForm, ResponsavelForm, TransporteAlunoForm, MatriculaForm

@login_required
def alunos_home(request):
    """
    Página inicial do módulo de Alunos com estatísticas e ações rápidas
    """
    # Estatísticas gerais
    total_alunos = Aluno.objects.count()
    arquivo_corrente = Aluno.objects.filter(tipo_arquivo='CORRENTE').count()
    arquivo_permanente = Aluno.objects.filter(tipo_arquivo='PERMANENTE').count()
    matriculas_ativas = Matricula.objects.filter(status='ATIVA').count()

    # Últimos 5 alunos cadastrados
    alunos_recentes = Aluno.objects.all().order_by('-codigo')[:5]

    # Distribuição das matrículas ativas por ano/série
    alunos_por_serie = []
    por_serie = Matricula.objects.filter(status='ATIVA').values('serie_ano').annotate(total=Count('id')).order_by('serie_ano')
    total_ativas = sum(item['total'] for item in por_serie)
    for item in por_serie:
        alunos_por_serie.append({
            'nome': item['serie_ano'],
            'total': item['total'],
            'percentual': item['total'] * 100 / total_ativas if total_ativas else 0,
        })

    context = {
        'total_alunos': total_alunos,
        'arquivo_corrente': arquivo_corrente,
        'arquivo_permanente': arquivo_permanente,
        'matriculas_ativas': matriculas_ativas,
        'alunos_recentes': alunos_recentes,
        'alunos_por_serie': alunos_por_serie,
    }

    return render(request, 'alunos/alunos_home.html', context)

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
    
    # Paginação - aumentando para 50 registros por página
    paginator = Paginator(alunos, 50)
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
                descricao='Novo aluno cadastrado no sistema'
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
                descricao='Dados básicos do aluno atualizados'
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
        descricao='Visualizou detalhes do aluno'
    )
    
    context = {
        'aluno': aluno,
        'documentacao': getattr(aluno, 'documentacao', None),
        'responsaveis': aluno.responsaveis.all(),
        'transporte': getattr(aluno, 'transporte', None),
        'matriculas': aluno.matriculas.all().order_by('-ano_administrativo'),
        'dados_adicionais': aluno.dados_adicionais.filter(dado_adicional__ativo=True).select_related(
            'dado_adicional').order_by('dado_adicional__ordem', 'dado_adicional__rotulo'),
    }

    return render(request, 'alunos/aluno_detail.html', context)

@login_required
def aluno_edit_extended(request, pk):
    """
    Cadastro estendido do aluno com abas (RF105):
    identificação, documentação, responsáveis e transporte.
    """
    aluno = get_object_or_404(Aluno, pk=pk)

    # Criar instâncias relacionadas se não existirem
    documentacao, _ = DocumentacaoAluno.objects.get_or_create(aluno=aluno)
    transporte, _ = TransporteAluno.objects.get_or_create(aluno=aluno)

    abas_validas = ('identificacao', 'documentacao', 'responsaveis', 'transporte', 'dados_adicionais')
    aba_ativa = request.GET.get('aba', 'identificacao')

    aluno_form = AlunoForm(instance=aluno, prefix='aluno')
    doc_form = DocumentacaoAlunoForm(instance=documentacao, prefix='doc')
    trans_form = TransporteAlunoForm(instance=transporte, prefix='trans')
    resp_form = ResponsavelForm(prefix='resp')
    adicionais_form = DadosAdicionaisAlunoForm(aluno=aluno, prefix='adic')

    if request.method == 'POST':
        aba_ativa = request.POST.get('aba_ativa', 'identificacao')
        form_salvo = None

        if aba_ativa == 'identificacao':
            aluno_form = AlunoForm(request.POST, request.FILES, instance=aluno, prefix='aluno')
            if aluno_form.is_valid():
                form_salvo = aluno_form.save()
                mensagem = 'Dados de identificação atualizados com sucesso.'
        elif aba_ativa == 'documentacao':
            doc_form = DocumentacaoAlunoForm(request.POST, instance=documentacao, prefix='doc')
            if doc_form.is_valid():
                form_salvo = doc_form.save()
                mensagem = 'Documentação atualizada com sucesso.'
        elif aba_ativa == 'transporte':
            trans_form = TransporteAlunoForm(request.POST, instance=transporte, prefix='trans')
            if trans_form.is_valid():
                form_salvo = trans_form.save()
                mensagem = 'Dados de transporte atualizados com sucesso.'
        elif aba_ativa == 'dados_adicionais':
            adicionais_form = DadosAdicionaisAlunoForm(request.POST, aluno=aluno, prefix='adic')
            if adicionais_form.is_valid():
                adicionais_form.save(request.user)
                form_salvo = True
                mensagem = 'Dados adicionais atualizados com sucesso.'
        elif aba_ativa == 'responsaveis':
            remover_id = request.POST.get('remover_responsavel')
            if remover_id:
                Responsavel.objects.filter(pk=remover_id, aluno=aluno).delete()
                form_salvo = True
                mensagem = 'Responsável removido.'
            else:
                resp_form = ResponsavelForm(request.POST, prefix='resp')
                if resp_form.is_valid():
                    responsavel = resp_form.save(commit=False)
                    responsavel.aluno = aluno
                    responsavel.save()
                    form_salvo = True
                    mensagem = 'Responsável adicionado com sucesso.'

        if form_salvo:
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='EDITAR',
                modulo='ALUNOS',
                objeto_nome=aluno.nome,
                objeto_id=aluno.codigo,
                descricao='Cadastro completo do aluno atualizado'
            )
            messages.success(request, mensagem)
            return redirect(f"{reverse('alunos:aluno_edit_extended', args=[aluno.pk])}?aba={aba_ativa}")
        messages.error(request, 'Corrija os erros destacados no formulário.')

    if aba_ativa not in abas_validas:
        aba_ativa = 'identificacao'

    context = {
        'aluno': aluno,
        'aluno_form': aluno_form,
        'doc_form': doc_form,
        'trans_form': trans_form,
        'resp_form': resp_form,
        'adicionais_form': adicionais_form,
        'responsaveis': aluno.responsaveis.all(),
        'aba_ativa': aba_ativa,
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
                descricao='Aluno removido do sistema'
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
