from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import ProjetoPedagogico, TurmaAEE, EnturmacaoAEE, HistoricoEnturmacao, AssociacaoEscola


@login_required
def aee_home(request):
    """
    Dashboard principal do módulo AEE/Atividade Complementar
    """
    # Estatísticas gerais
    total_projetos = ProjetoPedagogico.objects.filter(ativo=True).count()
    total_turmas = TurmaAEE.objects.filter(situacao='ATIVO').count()
    total_enturmacoes = EnturmacaoAEE.objects.filter(ativo=True).count()
    total_alunos_aee = EnturmacaoAEE.objects.filter(ativo=True).values('aluno').distinct().count()
    
    # Projetos recentes
    projetos_recentes = ProjetoPedagogico.objects.filter(ativo=True).order_by('-data_criacao')[:5]
    
    # Turmas ativas
    turmas_ativas = TurmaAEE.objects.filter(situacao='ATIVO').order_by('nome')[:5]
    
    context = {
        'total_projetos': total_projetos,
        'total_turmas': total_turmas,
        'total_enturmacoes': total_enturmacoes,
        'total_alunos_aee': total_alunos_aee,
        'projetos_recentes': projetos_recentes,
        'turmas_ativas': turmas_ativas,
    }
    
    return render(request, 'aee/home.html', context)


@login_required
def projetos_list(request):
    """
    Lista todos os projetos pedagógicos
    """
    projetos = ProjetoPedagogico.objects.all().order_by('-data_criacao')
    
    # Filtros
    tipo_projeto = request.GET.get('tipo', '')
    periodo_letivo = request.GET.get('periodo', '')
    
    if tipo_projeto:
        projetos = projetos.filter(tipo_projeto=tipo_projeto)
    if periodo_letivo:
        projetos = projetos.filter(periodo_letivo=periodo_letivo)
    
    context = {
        'projetos': projetos,
        'tipo_projeto': tipo_projeto,
        'periodo_letivo': periodo_letivo,
    }
    
    return render(request, 'aee/projetos_list.html', context)


@login_required
def projeto_create(request):
    """
    Criar novo projeto pedagógico
    """
    if request.method == 'POST':
        nome = request.POST.get('nome')
        tipo_projeto = request.POST.get('tipo_projeto')
        periodo_letivo = request.POST.get('periodo_letivo', '2025')
        descricao = request.POST.get('descricao', '')
        carga_horaria = request.POST.get('carga_horaria', 20)
        
        if nome and tipo_projeto:
            ProjetoPedagogico.objects.create(
                nome=nome,
                tipo_projeto=tipo_projeto,
                periodo_letivo=periodo_letivo,
                descricao=descricao,
                carga_horaria=carga_horaria,
                usuario_criacao=request.user
            )
            messages.success(request, 'Projeto pedagógico criado com sucesso!')
            return redirect('aee:projetos_list')
    
    return render(request, 'aee/projeto_form.html', {
        'title': 'Novo Projeto Pedagógico',
        'is_create': True
    })


@login_required
def projeto_detail(request, pk):
    """
    Detalhes de um projeto pedagógico
    """
    projeto = get_object_or_404(ProjetoPedagogico, pk=pk)
    turmas = projeto.turmas.all()
    
    context = {
        'projeto': projeto,
        'turmas': turmas,
    }
    
    return render(request, 'aee/projeto_detail.html', context)


@login_required
def projeto_edit(request, pk):
    """
    Editar projeto pedagógico
    """
    projeto = get_object_or_404(ProjetoPedagogico, pk=pk)
    
    if request.method == 'POST':
        projeto.nome = request.POST.get('nome', projeto.nome)
        projeto.tipo_projeto = request.POST.get('tipo_projeto', projeto.tipo_projeto)
        projeto.periodo_letivo = request.POST.get('periodo_letivo', projeto.periodo_letivo)
        projeto.descricao = request.POST.get('descricao', projeto.descricao)
        projeto.carga_horaria = request.POST.get('carga_horaria', projeto.carga_horaria)
        projeto.ativo = request.POST.get('ativo') == 'on'
        projeto.save()
        
        messages.success(request, 'Projeto atualizado com sucesso!')
        return redirect('aee:projeto_detail', pk=projeto.pk)
    
    context = {
        'projeto': projeto,
        'title': f'Editar Projeto - {projeto.nome}',
        'is_create': False
    }
    
    return render(request, 'aee/projeto_form.html', context)


@login_required
def turmas_list(request):
    """
    Lista todas as turmas AEE
    """
    turmas = TurmaAEE.objects.all().order_by('-data_criacao')
    
    context = {
        'turmas': turmas,
    }
    
    return render(request, 'aee/turmas_list.html', context)


@login_required
def turma_create(request):
    """
    Criar nova turma AEE
    """
    projetos = ProjetoPedagogico.objects.filter(ativo=True)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        projeto_id = request.POST.get('projeto_pedagogico')
        turno = request.POST.get('turno')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fim = request.POST.get('hora_fim')
        
        if nome and projeto_id and turno:
            projeto = get_object_or_404(ProjetoPedagogico, id=projeto_id)
            TurmaAEE.objects.create(
                nome=nome,
                projeto_pedagogico=projeto,
                periodo_letivo='2025',
                turno=turno,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
                usuario_criacao=request.user
            )
            messages.success(request, 'Turma criada com sucesso!')
            return redirect('aee:turmas_list')
    
    context = {
        'projetos': projetos,
        'title': 'Nova Turma AEE',
        'is_create': True
    }
    
    return render(request, 'aee/turma_form.html', context)


@login_required
def turma_detail(request, pk):
    """
    Detalhes de uma turma AEE
    """
    turma = get_object_or_404(TurmaAEE, pk=pk)
    enturmacoes = turma.enturmacoes.filter(ativo=True)
    
    context = {
        'turma': turma,
        'enturmacoes': enturmacoes,
    }
    
    return render(request, 'aee/turma_detail.html', context)


@login_required
def turma_edit(request, pk):
    """
    Editar turma AEE
    """
    turma = get_object_or_404(TurmaAEE, pk=pk)
    projetos = ProjetoPedagogico.objects.filter(ativo=True)
    
    if request.method == 'POST':
        turma.nome = request.POST.get('nome', turma.nome)
        projeto_id = request.POST.get('projeto_pedagogico')
        if projeto_id:
            turma.projeto_pedagogico_id = projeto_id
        turma.turno = request.POST.get('turno', turma.turno)
        turma.hora_inicio = request.POST.get('hora_inicio', turma.hora_inicio)
        turma.hora_fim = request.POST.get('hora_fim', turma.hora_fim)
        turma.situacao = request.POST.get('situacao', turma.situacao)
        turma.save()
        
        messages.success(request, 'Turma atualizada com sucesso!')
        return redirect('aee:turma_detail', pk=turma.pk)
    
    context = {
        'turma': turma,
        'projetos': projetos,
        'title': f'Editar Turma - {turma.nome}',
        'is_create': False
    }
    
    return render(request, 'aee/turma_form.html', context)


@login_required
def enturmacoes_list(request):
    """
    Lista todas as enturmações
    """
    enturmacoes = EnturmacaoAEE.objects.filter(ativo=True).order_by('-data_enturmacao')
    
    context = {
        'enturmacoes': enturmacoes,
    }
    
    return render(request, 'aee/enturmacoes_list.html', context)


@login_required
def enturmacao_create(request):
    """
    Criar nova enturmação
    """
    turmas = TurmaAEE.objects.filter(situacao='ATIVO')
    
    if request.method == 'POST':
        # Implementar lógica de enturmação
        messages.success(request, 'Enturmação realizada com sucesso!')
        return redirect('aee:enturmacoes_list')
    
    context = {
        'turmas': turmas,
        'title': 'Nova Enturmação',
        'is_create': True
    }
    
    return render(request, 'aee/enturmacao_form.html', context)