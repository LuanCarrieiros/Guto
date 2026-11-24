from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from dashboard.models import AtividadeRecente
from .forms import EnturmacaoAEEForm, ProjetoPedagogicoForm, TurmaAEEForm
from .models import EnturmacaoAEE, HistoricoEnturmacao, ProjetoPedagogico, TurmaAEE


def registrar(request, acao, objeto, descricao):
    AtividadeRecente.registrar_atividade(
        usuario=request.user, acao=acao, modulo='AEE',
        objeto_nome=str(objeto), objeto_id=objeto.pk, descricao=descricao,
    )


@login_required
def aee_home(request):
    """
    Dashboard principal do módulo AEE/Atividade Complementar
    """
    context = {
        'total_projetos': ProjetoPedagogico.objects.filter(ativo=True).count(),
        'total_turmas': TurmaAEE.objects.filter(situacao='ATIVO').count(),
        'total_enturmacoes': EnturmacaoAEE.objects.filter(ativo=True).count(),
        'total_alunos_aee': EnturmacaoAEE.objects.filter(ativo=True).values('aluno').distinct().count(),
        'projetos_recentes': ProjetoPedagogico.objects.filter(ativo=True).order_by('-data_criacao')[:5],
        'turmas_ativas': TurmaAEE.objects.filter(situacao='ATIVO').order_by('nome')[:5],
    }
    return render(request, 'aee/home.html', context)


# ============================== PROJETOS ==============================

@login_required
def projetos_list(request):
    """
    Lista todos os projetos pedagógicos
    """
    projetos = ProjetoPedagogico.objects.annotate(total_turmas=Count('turmaaee')).order_by('-periodo_letivo', 'nome')
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
        'tipos': ProjetoPedagogico.TIPO_PROJETO_CHOICES,
        'periodos': ProjetoPedagogico.objects.order_by('-periodo_letivo').values_list('periodo_letivo', flat=True).distinct(),
    }
    return render(request, 'aee/projetos_list.html', context)


@login_required
def projeto_create(request):
    """
    Criar novo projeto pedagógico
    """
    form = ProjetoPedagogicoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        projeto = form.save(commit=False)
        projeto.usuario_criacao = request.user
        projeto.save()
        registrar(request, 'CRIAR', projeto, 'Novo projeto pedagógico')
        messages.success(request, 'Projeto pedagógico criado com sucesso!')
        return redirect('aee:projeto_detail', pk=projeto.pk)

    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Novo Projeto Pedagógico',
        'subtitle': 'Projeto de AEE ou Atividade Complementar',
        'icon': 'fa-lightbulb',
        'cancel_url': reverse('aee:projetos_list'),
        'submit_label': 'Criar projeto',
    })


@login_required
def projeto_detail(request, pk):
    """
    Detalhes de um projeto pedagógico
    """
    projeto = get_object_or_404(ProjetoPedagogico, pk=pk)
    turmas = TurmaAEE.objects.filter(projeto_pedagogico=projeto).annotate(
        total_alunos=Count('enturmacoes', filter=Q(enturmacoes__ativo=True))
    ).order_by('nome')
    return render(request, 'aee/projeto_detail.html', {'projeto': projeto, 'turmas': turmas})


@login_required
def projeto_edit(request, pk):
    """
    Editar projeto pedagógico
    """
    projeto = get_object_or_404(ProjetoPedagogico, pk=pk)
    form = ProjetoPedagogicoForm(request.POST or None, instance=projeto)
    if request.method == 'POST' and form.is_valid():
        form.save()
        registrar(request, 'EDITAR', projeto, 'Projeto pedagógico atualizado')
        messages.success(request, 'Projeto atualizado com sucesso!')
        return redirect('aee:projeto_detail', pk=projeto.pk)

    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Editar Projeto Pedagógico',
        'subtitle': projeto.nome,
        'icon': 'fa-lightbulb',
        'cancel_url': reverse('aee:projeto_detail', args=[projeto.pk]),
    })


# ============================== TURMAS ==============================

@login_required
def turmas_list(request):
    """
    Lista todas as turmas AEE
    """
    turmas = TurmaAEE.objects.select_related('projeto_pedagogico').annotate(
        total_alunos=Count('enturmacoes', filter=Q(enturmacoes__ativo=True))
    ).order_by('-periodo_letivo', 'nome')
    situacao = request.GET.get('situacao', '')
    if situacao:
        turmas = turmas.filter(situacao=situacao)
    return render(request, 'aee/turmas_list.html', {
        'turmas': turmas,
        'situacao': situacao,
        'situacoes': TurmaAEE.SITUACAO_CHOICES,
    })


@login_required
def turma_create(request):
    """
    Criar nova turma AEE
    """
    form = TurmaAEEForm(request.POST or None, initial={'projeto_pedagogico': request.GET.get('projeto')})
    if request.method == 'POST' and form.is_valid():
        turma = form.save(commit=False)
        turma.usuario_criacao = request.user
        turma.save()
        registrar(request, 'CRIAR', turma, 'Nova turma de AEE/AC')
        messages.success(request, 'Turma criada com sucesso!')
        return redirect('aee:turma_detail', pk=turma.pk)

    if not ProjetoPedagogico.objects.filter(ativo=True).exists():
        messages.warning(request, 'Cadastre um projeto pedagógico ativo antes de criar turmas.')
    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Nova Turma AEE/AC',
        'icon': 'fa-users',
        'cancel_url': reverse('aee:turmas_list'),
        'submit_label': 'Criar turma',
    })


@login_required
def turma_detail(request, pk):
    """
    Detalhes de uma turma AEE
    """
    turma = get_object_or_404(TurmaAEE.objects.select_related('projeto_pedagogico'), pk=pk)
    ordenacao = {
        'ALFABETICA': 'aluno__nome',
        'DATA_NASCIMENTO': 'aluno__data_nascimento',
        'CODIGO': 'aluno__codigo',
    }.get(turma.ordenacao, 'data_enturmacao')
    enturmacoes = turma.enturmacoes.filter(ativo=True).select_related('aluno').order_by(ordenacao)
    context = {
        'turma': turma,
        'enturmacoes': enturmacoes,
        'historico': turma.historico.select_related('aluno', 'usuario')[:15],
        'vagas_restantes': max(turma.maximo_alunos - enturmacoes.count(), 0),
    }
    return render(request, 'aee/turma_detail.html', context)


@login_required
def turma_edit(request, pk):
    """
    Editar turma AEE
    """
    turma = get_object_or_404(TurmaAEE, pk=pk)
    form = TurmaAEEForm(request.POST or None, instance=turma)
    if request.method == 'POST' and form.is_valid():
        form.save()
        registrar(request, 'EDITAR', turma, 'Turma de AEE/AC atualizada')
        messages.success(request, 'Turma atualizada com sucesso!')
        return redirect('aee:turma_detail', pk=turma.pk)

    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Editar Turma AEE/AC',
        'subtitle': turma.nome,
        'icon': 'fa-users',
        'cancel_url': reverse('aee:turma_detail', args=[turma.pk]),
    })


# ============================== ENTURMAÇÕES ==============================

@login_required
def enturmacoes_list(request):
    """
    Lista todas as enturmações ativas
    """
    enturmacoes = EnturmacaoAEE.objects.filter(ativo=True).select_related(
        'aluno', 'turma', 'turma__projeto_pedagogico'
    ).order_by('turma__nome', 'aluno__nome')
    busca = request.GET.get('q', '').strip()
    if busca:
        enturmacoes = enturmacoes.filter(Q(aluno__nome__icontains=busca) | Q(turma__nome__icontains=busca))
    return render(request, 'aee/enturmacoes_list.html', {'enturmacoes': enturmacoes, 'busca': busca})


@login_required
def enturmacao_create(request):
    """
    Enturmar aluno em turma AEE/AC (RF901-RF908)
    """
    turma_inicial = request.GET.get('turma')
    form = EnturmacaoAEEForm(request.POST or None, initial={
        'turma': turma_inicial,
        'origem': 'PROPRIA_ESCOLA',
        'ano_administrativo': str(timezone.localdate().year),
    })
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            enturmacao = form.save(commit=False)
            enturmacao.usuario_enturmacao = request.user
            enturmacao.save()
            HistoricoEnturmacao.objects.create(
                turma=enturmacao.turma, aluno=enturmacao.aluno, acao='ADICIONAR', usuario=request.user,
            )
        messages.success(request, f'{enturmacao.aluno.nome} enturmado(a) em {enturmacao.turma.nome}.')
        return redirect('aee:turma_detail', pk=enturmacao.turma.pk)

    cancelar = reverse('aee:turma_detail', args=[turma_inicial]) if turma_inicial else reverse('aee:enturmacoes_list')
    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Nova Enturmação AEE/AC',
        'subtitle': 'Vincule um aluno a uma turma de AEE ou Atividade Complementar',
        'icon': 'fa-user-plus',
        'cancel_url': cancelar,
        'submit_label': 'Enturmar',
    })


@login_required
@require_POST
def enturmacao_remover(request, pk):
    """
    Retira o aluno da turma, mantendo o registro histórico
    """
    enturmacao = get_object_or_404(EnturmacaoAEE, pk=pk, ativo=True)
    with transaction.atomic():
        # Garante a unicidade (turma, aluno, ativo) ao inativar
        EnturmacaoAEE.objects.filter(turma=enturmacao.turma, aluno=enturmacao.aluno, ativo=False).delete()
        enturmacao.ativo = False
        enturmacao.data_saida = timezone.now()
        enturmacao.save()
        HistoricoEnturmacao.objects.create(
            turma=enturmacao.turma, aluno=enturmacao.aluno, acao='REMOVER', usuario=request.user,
            observacoes=request.POST.get('observacoes') or None,
        )
    messages.success(request, f'{enturmacao.aluno.nome} retirado(a) da turma {enturmacao.turma.nome}.')
    return redirect('aee:turma_detail', pk=enturmacao.turma.pk)
