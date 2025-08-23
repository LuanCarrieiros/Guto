from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from dashboard.models import AtividadeRecente
from alunos.models import Aluno
from .models import ItinerarioFormativo, UnidadeCurricular, AssociacaoItinerarioUnidade, EnturmacaoItinerario
from .forms import ItinerarioFormativoForm, UnidadeCurricularForm, EnturmacaoItinerarioForm

@login_required
def escola_home(request):
    """
    Página inicial do módulo Escola
    """
    context = {
        'total_itinerarios': ItinerarioFormativo.objects.count(),
        'total_unidades': UnidadeCurricular.objects.count(),
        'total_enturmacoes': EnturmacaoItinerario.objects.count(),
        'itinerarios_recentes': ItinerarioFormativo.objects.all()[:5],
    }
    return render(request, 'escola/escola_home.html', context)

# Views para Itinerários Formativos
@login_required
def itinerario_list(request):
    """
    Lista todos os itinerários formativos
    """
    itinerarios = ItinerarioFormativo.objects.annotate(
        total_alunos=Count('alunos')
    ).all()
    
    # Filtros
    busca = request.GET.get('busca')
    area_conhecimento = request.GET.get('area_conhecimento')
    
    if busca:
        itinerarios = itinerarios.filter(
            Q(nome__icontains=busca) | Q(habilidades__icontains=busca)
        )
    
    if area_conhecimento and area_conhecimento != 'TODAS':
        itinerarios = itinerarios.filter(areas_conhecimento=area_conhecimento)
    
    # Paginação
    paginator = Paginator(itinerarios, 20)
    page_number = request.GET.get('page')
    itinerarios_page = paginator.get_page(page_number)
    
    context = {
        'itinerarios': itinerarios_page,
        'busca': busca or '',
        'area_conhecimento': area_conhecimento or 'TODAS',
        'areas_choices': ItinerarioFormativo.AREA_CONHECIMENTO_CHOICES,
    }
    
    return render(request, 'escola/itinerario_list.html', context)

@login_required
def itinerario_create(request):
    """
    Criar novo itinerário formativo
    """
    if request.method == 'POST':
        form = ItinerarioFormativoForm(request.POST)
        if form.is_valid():
            itinerario = form.save(commit=False)
            itinerario.usuario_cadastro = request.user
            itinerario.save()
            
            # Registrar atividade recente
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='CRIAR',
                modulo='ESCOLA',
                objeto_nome=itinerario.nome,
                objeto_id=str(itinerario.pk),
                descricao=f'Novo itinerário formativo cadastrado'
            )
            
            messages.success(request, 'Itinerário formativo criado com sucesso.')
            return redirect('escola:itinerario_detail', pk=itinerario.pk)
    else:
        form = ItinerarioFormativoForm()
    
    return render(request, 'escola/itinerario_form.html', {
        'form': form,
        'title': 'Novo Itinerário Formativo',
        'is_create': True
    })

@login_required
def itinerario_detail(request, pk):
    """
    Visualizar detalhes do itinerário formativo
    """
    itinerario = get_object_or_404(ItinerarioFormativo, pk=pk)
    
    # Registrar atividade recente
    AtividadeRecente.registrar_atividade(
        usuario=request.user,
        acao='VISUALIZAR',
        modulo='ESCOLA',
        objeto_nome=itinerario.nome,
        objeto_id=str(itinerario.pk),
        descricao=f'Visualizou detalhes do itinerário formativo'
    )
    
    context = {
        'itinerario': itinerario,
        'unidades': itinerario.unidades.select_related('unidade').order_by('ordem'),
        'alunos_enturmados': itinerario.alunos.select_related('aluno').all()[:10],
        'total_alunos': itinerario.alunos.count(),
        'vagas_restantes': itinerario.vagas_disponiveis - itinerario.alunos.count(),
    }
    
    return render(request, 'escola/itinerario_detail.html', context)

@login_required
def itinerario_edit(request, pk):
    """
    Editar itinerário formativo
    """
    itinerario = get_object_or_404(ItinerarioFormativo, pk=pk)
    
    if request.method == 'POST':
        form = ItinerarioFormativoForm(request.POST, instance=itinerario)
        if form.is_valid():
            form.save()
            
            # Registrar atividade recente
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='EDITAR',
                modulo='ESCOLA',
                objeto_nome=itinerario.nome,
                objeto_id=str(itinerario.pk),
                descricao=f'Itinerário formativo atualizado'
            )
            
            messages.success(request, 'Itinerário formativo atualizado com sucesso.')
            return redirect('escola:itinerario_detail', pk=itinerario.pk)
    else:
        form = ItinerarioFormativoForm(instance=itinerario)
    
    return render(request, 'escola/itinerario_form.html', {
        'form': form,
        'itinerario': itinerario,
        'title': f'Editar - {itinerario.nome}',
        'is_create': False
    })

# Views para Unidades Curriculares
@login_required
def unidade_list(request):
    """
    Lista todas as unidades curriculares
    """
    unidades = UnidadeCurricular.objects.all()
    
    # Filtros
    busca = request.GET.get('busca')
    
    if busca:
        unidades = unidades.filter(
            Q(nome__icontains=busca) | Q(ementa__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(unidades, 20)
    page_number = request.GET.get('page')
    unidades_page = paginator.get_page(page_number)
    
    context = {
        'unidades': unidades_page,
        'busca': busca or '',
    }
    
    return render(request, 'escola/unidade_list.html', context)

@login_required
def unidade_create(request):
    """
    Criar nova unidade curricular
    """
    if request.method == 'POST':
        form = UnidadeCurricularForm(request.POST)
        if form.is_valid():
            unidade = form.save(commit=False)
            unidade.usuario_cadastro = request.user
            unidade.save()
            
            messages.success(request, 'Unidade curricular criada com sucesso.')
            return redirect('escola:unidade_detail', pk=unidade.pk)
    else:
        form = UnidadeCurricularForm()
    
    return render(request, 'escola/unidade_form.html', {
        'form': form,
        'title': 'Nova Unidade Curricular',
        'is_create': True
    })

@login_required
def unidade_detail(request, pk):
    """
    Visualizar detalhes da unidade curricular
    """
    unidade = get_object_or_404(UnidadeCurricular, pk=pk)
    
    context = {
        'unidade': unidade,
        'itinerarios_associados': unidade.associacaoitinerariounidade_set.select_related('itinerario').all(),
    }
    
    return render(request, 'escola/unidade_detail.html', context)

# Views para Enturmação
@login_required
def enturmacao_create(request, itinerario_pk):
    """
    Enturmar aluno em itinerário formativo
    """
    itinerario = get_object_or_404(ItinerarioFormativo, pk=itinerario_pk)
    
    if request.method == 'POST':
        form = EnturmacaoItinerarioForm(request.POST)
        if form.is_valid():
            aluno = form.cleaned_data['aluno']
            
            # Verificar se já existe enturmação
            if EnturmacaoItinerario.objects.filter(aluno=aluno, itinerario=itinerario).exists():
                messages.error(request, f'O aluno {aluno.nome} já está enturmado neste itinerário.')
                return redirect('escola:itinerario_detail', pk=itinerario.pk)
            
            # Verificar vagas disponíveis
            total_enturmados = itinerario.alunos.count()
            if total_enturmados >= itinerario.vagas_disponiveis:
                messages.error(request, 'Não há vagas disponíveis neste itinerário.')
                return redirect('escola:itinerario_detail', pk=itinerario.pk)
            
            enturmacao = form.save(commit=False)
            enturmacao.itinerario = itinerario
            enturmacao.usuario_enturmacao = request.user
            enturmacao.save()
            
            messages.success(request, f'Aluno {aluno.nome} enturmado com sucesso.')
            return redirect('escola:itinerario_detail', pk=itinerario.pk)
    else:
        form = EnturmacaoItinerarioForm()
    
    return render(request, 'escola/enturmacao_form.html', {
        'form': form,
        'itinerario': itinerario,
        'title': f'Enturmar Aluno - {itinerario.nome}'
    })

@login_required
def enturmacao_delete(request, pk):
    """
    Remover aluno do itinerário formativo
    """
    enturmacao = get_object_or_404(EnturmacaoItinerario, pk=pk)
    itinerario = enturmacao.itinerario
    
    if request.method == 'POST':
        if request.POST.get('confirmar') == 'sim':
            aluno_nome = enturmacao.aluno.nome
            enturmacao.delete()
            
            messages.success(request, f'Aluno {aluno_nome} removido do itinerário.')
            return redirect('escola:itinerario_detail', pk=itinerario.pk)
    
    return render(request, 'escola/enturmacao_confirm_delete.html', {
        'enturmacao': enturmacao
    })
