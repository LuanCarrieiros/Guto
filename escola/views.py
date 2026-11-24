from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from dashboard.models import AtividadeRecente
from .forms import (
    AssociacaoUnidadeForm, EnturmacaoItinerarioForm, ItinerarioFormativoForm, UnidadeCurricularForm,
)
from .models import AssociacaoItinerarioUnidade, EnturmacaoItinerario, ItinerarioFormativo, UnidadeCurricular


def registrar(request, acao, objeto, descricao):
    AtividadeRecente.registrar_atividade(
        usuario=request.user, acao=acao, modulo='ESCOLA',
        objeto_nome=str(objeto), objeto_id=objeto.pk, descricao=descricao,
    )


@login_required
def escola_home(request):
    """
    Página inicial do módulo Escola
    """
    total_vagas = ItinerarioFormativo.objects.aggregate(total=Sum('vagas_disponiveis'))['total'] or 0
    total_enturmacoes = EnturmacaoItinerario.objects.count()
    context = {
        'total_itinerarios': ItinerarioFormativo.objects.count(),
        'total_unidades': UnidadeCurricular.objects.count(),
        'total_enturmacoes': total_enturmacoes,
        'taxa_ocupacao': round(total_enturmacoes * 100 / total_vagas) if total_vagas else 0,
        'itinerarios_recentes': ItinerarioFormativo.objects.order_by('-data_cadastro')[:5],
    }
    return render(request, 'escola/escola_home.html', context)


# ============================== ITINERÁRIOS ==============================

@login_required
def itinerario_list(request):
    """
    Lista todos os itinerários formativos
    """
    itinerarios = ItinerarioFormativo.objects.annotate(
        total_alunos=Count('alunos', distinct=True),
        total_unidades=Count('unidades', distinct=True),
    ).order_by('nome')

    busca = request.GET.get('busca', '').strip()
    area_conhecimento = request.GET.get('area_conhecimento', '')
    if busca:
        itinerarios = itinerarios.filter(Q(nome__icontains=busca) | Q(habilidades__icontains=busca))
    if area_conhecimento:
        itinerarios = itinerarios.filter(areas_conhecimento=area_conhecimento)

    context = {
        'page_obj': Paginator(itinerarios, 20).get_page(request.GET.get('page')),
        'busca': busca,
        'area_conhecimento': area_conhecimento,
        'areas_choices': ItinerarioFormativo.AREA_CONHECIMENTO_CHOICES,
    }
    return render(request, 'escola/itinerario_list.html', context)


@login_required
def itinerario_create(request):
    """
    Criar novo itinerário formativo
    """
    form = ItinerarioFormativoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        itinerario = form.save(commit=False)
        itinerario.usuario_cadastro = request.user
        itinerario.save()
        registrar(request, 'CRIAR', itinerario, 'Novo itinerário formativo cadastrado')
        messages.success(request, 'Itinerário formativo criado com sucesso.')
        return redirect('escola:itinerario_detail', pk=itinerario.pk)

    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Novo Itinerário Formativo',
        'icon': 'fa-route',
        'cancel_url': reverse('escola:itinerario_list'),
        'submit_label': 'Criar itinerário',
    })


@login_required
def itinerario_detail(request, pk):
    """
    Visualizar detalhes do itinerário formativo
    """
    itinerario = get_object_or_404(ItinerarioFormativo, pk=pk)
    total_alunos = itinerario.alunos.count()
    context = {
        'itinerario': itinerario,
        'unidades': itinerario.unidades.select_related('unidade').order_by('ordem'),
        'alunos_enturmados': itinerario.alunos.select_related('aluno', 'usuario_enturmacao').order_by('aluno__nome'),
        'total_alunos': total_alunos,
        'vagas_restantes': max(itinerario.vagas_disponiveis - total_alunos, 0),
        'carga_unidades': itinerario.unidades.aggregate(total=Sum('unidade__carga_horaria'))['total'] or 0,
        'associacao_form': AssociacaoUnidadeForm(itinerario=itinerario),
    }
    return render(request, 'escola/itinerario_detail.html', context)


@login_required
def itinerario_edit(request, pk):
    """
    Editar itinerário formativo
    """
    itinerario = get_object_or_404(ItinerarioFormativo, pk=pk)
    form = ItinerarioFormativoForm(request.POST or None, instance=itinerario)
    if request.method == 'POST' and form.is_valid():
        form.save()
        registrar(request, 'EDITAR', itinerario, 'Itinerário formativo atualizado')
        messages.success(request, 'Itinerário formativo atualizado com sucesso.')
        return redirect('escola:itinerario_detail', pk=itinerario.pk)

    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Editar Itinerário Formativo',
        'subtitle': itinerario.nome,
        'icon': 'fa-route',
        'cancel_url': reverse('escola:itinerario_detail', args=[itinerario.pk]),
    })


@login_required
@require_POST
def associar_unidade(request, itinerario_pk):
    """Adiciona uma unidade curricular à grade do itinerário"""
    itinerario = get_object_or_404(ItinerarioFormativo, pk=itinerario_pk)
    form = AssociacaoUnidadeForm(request.POST, itinerario=itinerario)
    if form.is_valid():
        associacao = form.save(commit=False)
        associacao.itinerario = itinerario
        associacao.save()
        messages.success(request, f'Unidade "{associacao.unidade}" adicionada ao itinerário.')
    else:
        for erros in form.errors.values():
            for erro in erros:
                messages.error(request, erro)
    return redirect('escola:itinerario_detail', pk=itinerario.pk)


@login_required
@require_POST
def desassociar_unidade(request, pk):
    """Remove uma unidade curricular da grade do itinerário"""
    associacao = get_object_or_404(AssociacaoItinerarioUnidade, pk=pk)
    itinerario_pk = associacao.itinerario_id
    associacao.delete()
    messages.success(request, 'Unidade removida do itinerário.')
    return redirect('escola:itinerario_detail', pk=itinerario_pk)


# ============================== UNIDADES CURRICULARES ==============================

@login_required
def unidade_list(request):
    """
    Lista todas as unidades curriculares
    """
    unidades = UnidadeCurricular.objects.annotate(
        total_itinerarios=Count('associacaoitinerariounidade')
    ).order_by('nome')
    busca = request.GET.get('busca', '').strip()
    if busca:
        unidades = unidades.filter(Q(nome__icontains=busca) | Q(ementa__icontains=busca))

    context = {
        'page_obj': Paginator(unidades, 20).get_page(request.GET.get('page')),
        'busca': busca,
    }
    return render(request, 'escola/unidade_list.html', context)


@login_required
def unidade_create(request):
    """
    Criar nova unidade curricular
    """
    form = UnidadeCurricularForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        unidade = form.save(commit=False)
        unidade.usuario_cadastro = request.user
        unidade.save()
        registrar(request, 'CRIAR', unidade, 'Nova unidade curricular cadastrada')
        messages.success(request, 'Unidade curricular criada com sucesso.')
        return redirect('escola:unidade_detail', pk=unidade.pk)

    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Nova Unidade Curricular',
        'icon': 'fa-book',
        'cancel_url': reverse('escola:unidade_list'),
        'submit_label': 'Criar unidade',
    })


@login_required
def unidade_edit(request, pk):
    """
    Editar unidade curricular
    """
    unidade = get_object_or_404(UnidadeCurricular, pk=pk)
    form = UnidadeCurricularForm(request.POST or None, instance=unidade)
    if request.method == 'POST' and form.is_valid():
        form.save()
        registrar(request, 'EDITAR', unidade, 'Unidade curricular atualizada')
        messages.success(request, 'Unidade curricular atualizada com sucesso.')
        return redirect('escola:unidade_detail', pk=unidade.pk)

    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Editar Unidade Curricular',
        'subtitle': unidade.nome,
        'icon': 'fa-book',
        'cancel_url': reverse('escola:unidade_detail', args=[unidade.pk]),
    })


@login_required
def unidade_detail(request, pk):
    """
    Visualizar detalhes da unidade curricular
    """
    unidade = get_object_or_404(UnidadeCurricular, pk=pk)
    context = {
        'unidade': unidade,
        'itinerarios_associados': unidade.associacaoitinerariounidade_set.select_related('itinerario'),
    }
    return render(request, 'escola/unidade_detail.html', context)


# ============================== ENTURMAÇÃO ==============================

@login_required
def enturmacao_create(request, itinerario_pk):
    """
    Enturmar aluno em itinerário formativo
    """
    itinerario = get_object_or_404(ItinerarioFormativo, pk=itinerario_pk)
    detalhe_url = reverse('escola:itinerario_detail', args=[itinerario.pk])

    if itinerario.alunos.count() >= itinerario.vagas_disponiveis:
        messages.error(request, 'Não há vagas disponíveis neste itinerário.')
        return redirect(detalhe_url)

    form = EnturmacaoItinerarioForm(request.POST or None, itinerario=itinerario)
    if request.method == 'POST' and form.is_valid():
        enturmacao = form.save(commit=False)
        enturmacao.itinerario = itinerario
        enturmacao.usuario_enturmacao = request.user
        enturmacao.save()
        messages.success(request, f'Aluno {enturmacao.aluno.nome} enturmado com sucesso.')
        return redirect(detalhe_url)

    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Enturmar Aluno',
        'subtitle': f'{itinerario.nome} · {itinerario.vagas_disponiveis - itinerario.alunos.count()} vaga(s) restante(s)',
        'icon': 'fa-user-plus',
        'cancel_url': detalhe_url,
        'submit_label': 'Enturmar',
    })


@login_required
def enturmacao_delete(request, pk):
    """
    Remover aluno do itinerário formativo
    """
    enturmacao = get_object_or_404(EnturmacaoItinerario.objects.select_related('aluno', 'itinerario'), pk=pk)
    itinerario = enturmacao.itinerario

    if request.method == 'POST' and request.POST.get('confirmar') == 'sim':
        aluno_nome = enturmacao.aluno.nome
        enturmacao.delete()
        messages.success(request, f'Aluno {aluno_nome} removido do itinerário.')
        return redirect('escola:itinerario_detail', pk=itinerario.pk)

    return render(request, 'generic/confirm_delete.html', {
        'title': 'Remover Aluno do Itinerário',
        'object_label': f'{enturmacao.aluno.nome} de "{itinerario.nome}"',
        'warning': 'O aluno deixará de ocupar uma vaga neste itinerário.',
        'cancel_url': reverse('escola:itinerario_detail', args=[itinerario.pk]),
    })
