from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg
from django.db import models
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import date
from .models import (
    Conceito, Turma, Disciplina, LancamentoNota, AtestadoMedico,
    MediaGlobalConceito, RecuperacaoEspecial, ParecerDescritivo,
    AvaliacaoDescritiva, PendenciaAvaliacao, DiarioOnline, ConteudoAula,
    Enturmacao
)
from .forms import TurmaForm, DisciplinaForm, EnturmacaoForm
from alunos.models import Aluno
from dashboard.models import AtividadeRecente


@login_required
def avaliacao_home(request):
    """
    Dashboard principal do módulo Avaliação
    """
    # Estatísticas gerais
    total_turmas = Turma.objects.count()
    total_disciplinas = Disciplina.objects.count()
    total_lancamentos = LancamentoNota.objects.count()
    pendencias = PendenciaAvaliacao.objects.filter(resolvida=False).count()
    
    # Turmas recentes
    turmas_recentes = Turma.objects.order_by('-id')[:5]
    
    # Lançamentos recentes
    lancamentos_recentes = LancamentoNota.objects.order_by('-data_lancamento')[:5]
    
    context = {
        'total_turmas': total_turmas,
        'total_disciplinas': total_disciplinas,
        'total_lancamentos': total_lancamentos,
        'pendencias': pendencias,
        'turmas_recentes': turmas_recentes,
        'lancamentos_recentes': lancamentos_recentes,
    }
    
    return render(request, 'avaliacao/home.html', context)


@login_required
def turmas_list(request):
    """
    Lista todas as turmas para avaliação
    """
    turmas = Turma.objects.all()
    
    # Filtros
    busca = request.GET.get('busca', '')
    periodo_letivo = request.GET.get('periodo_letivo', '')
    tipo_ensino = request.GET.get('tipo_ensino', '')
    turno = request.GET.get('turno', '')
    
    if busca:
        turmas = turmas.filter(nome__icontains=busca)
    if periodo_letivo:
        turmas = turmas.filter(periodo_letivo=periodo_letivo)
    if tipo_ensino:
        turmas = turmas.filter(tipo_ensino=tipo_ensino)
    if turno:
        turmas = turmas.filter(turno=turno)
    
    # Paginação
    paginator = Paginator(turmas, 25)
    page_number = request.GET.get('page')
    turmas_page = paginator.get_page(page_number)
    
    # Estatísticas
    total_turmas = Turma.objects.count()
    total_alunos_enturmados = Enturmacao.objects.filter(ativo=True).count()
    
    context = {
        'turmas': turmas_page,
        'busca': busca,
        'periodo_letivo': periodo_letivo,
        'tipo_ensino': tipo_ensino,
        'turno': turno,
        'total_turmas': total_turmas,
        'total_alunos_enturmados': total_alunos_enturmados,
        'tipo_ensino_choices': Turma.TIPO_ENSINO_CHOICES,
        'turno_choices': Turma.TURNO_CHOICES,
    }
    
    return render(request, 'avaliacao/turmas_list.html', context)


@login_required
def turma_create(request):
    """
    Criar nova turma
    """
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            turma = form.save(commit=False)
            turma.usuario_criacao = request.user
            turma.save()
            
            # Registrar atividade recente
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='CRIAR',
                modulo='AVALIACAO',
                objeto_nome=turma.nome,
                objeto_id=turma.id,
                descricao=f'Nova turma criada: {turma.nome}'
            )
            
            messages.success(request, 'Turma criada com sucesso!')
            return redirect('avaliacao:turmas_list')
    else:
        form = TurmaForm()
    
    return render(request, 'avaliacao/turma_form.html', {
        'form': form,
        'title': 'Criar Nova Turma',
        'is_create': True
    })


@login_required
def turma_edit(request, pk):
    """
    Editar turma
    """
    turma = get_object_or_404(Turma, pk=pk)
    
    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma)
        if form.is_valid():
            form.save()
            
            # Registrar atividade recente
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='EDITAR',
                modulo='AVALIACAO',
                objeto_nome=turma.nome,
                objeto_id=turma.id,
                descricao=f'Turma editada: {turma.nome}'
            )
            
            messages.success(request, 'Turma editada com sucesso!')
            return redirect('avaliacao:turma_detail', pk=turma.pk)
    else:
        form = TurmaForm(instance=turma)
    
    return render(request, 'avaliacao/turma_form.html', {
        'form': form,
        'turma': turma,
        'title': f'Editar Turma - {turma.nome}',
        'is_create': False
    })


@login_required
def turma_detail(request, pk):
    """
    Visualizar detalhes da turma
    """
    turma = get_object_or_404(Turma, pk=pk)
    
    # Alunos enturmados
    enturmacoes = Enturmacao.objects.filter(turma=turma, ativo=True).select_related('aluno')
    
    # Estatísticas
    total_enturmados = enturmacoes.count()
    vagas_disponiveis = turma.vagas_total - total_enturmados
    
    context = {
        'turma': turma,
        'enturmacoes': enturmacoes,
        'total_enturmados': total_enturmados,
        'vagas_disponiveis': vagas_disponiveis,
    }
    
    return render(request, 'avaliacao/turma_detail.html', context)


@login_required
def turma_delete(request, pk):
    """
    Excluir turma
    """
    turma = get_object_or_404(Turma, pk=pk)
    
    # Verificar se há alunos enturmados
    if turma.enturmacoes.filter(ativo=True).exists():
        messages.error(request, 'Não é possível excluir uma turma que possui alunos enturmados.')
        return redirect('avaliacao:turma_detail', pk=turma.pk)
    
    if request.method == 'POST':
        nome_turma = turma.nome
        turma.delete()
        
        # Registrar atividade recente
        AtividadeRecente.registrar_atividade(
            usuario=request.user,
            acao='DELETAR',
            modulo='AVALIACAO',
            objeto_nome=nome_turma,
            objeto_id=pk,
            descricao=f'Turma excluída: {nome_turma}'
        )
        
        messages.success(request, f'Turma {nome_turma} excluída com sucesso!')
        return redirect('avaliacao:turmas_list')
    
    return render(request, 'avaliacao/turma_confirm_delete.html', {'turma': turma})


@login_required
def disciplinas_list(request):
    """
    Lista todas as disciplinas
    """
    disciplinas = Disciplina.objects.all().order_by('nome')
    
    context = {
        'disciplinas': disciplinas,
    }
    
    return render(request, 'avaliacao/disciplinas_list.html', context)


@login_required
def notas_list(request):
    """
    Lista lançamentos de notas
    """
    lancamentos = LancamentoNota.objects.all().order_by('-data_lancamento')
    
    # Filtros
    turma_id = request.GET.get('turma', '')
    disciplina_id = request.GET.get('disciplina', '')
    
    if turma_id:
        lancamentos = lancamentos.filter(turma_id=turma_id)
    if disciplina_id:
        lancamentos = lancamentos.filter(disciplina_id=disciplina_id)
    
    turmas = Turma.objects.all()
    disciplinas = Disciplina.objects.all()
    
    context = {
        'lancamentos': lancamentos,
        'turmas': turmas,
        'disciplinas': disciplinas,
        'turma_selecionada': turma_id,
        'disciplina_selecionada': disciplina_id,
    }
    
    return render(request, 'avaliacao/notas_list.html', context)


@login_required
def lancar_notas(request):
    """
    Formulário para lançar notas
    """
    turmas = Turma.objects.all()
    disciplinas = Disciplina.objects.all()
    conceitos = Conceito.objects.filter(ativo=True)
    
    if request.method == 'POST':
        turma_id = request.POST.get('turma')
        disciplina_id = request.POST.get('disciplina')
        aluno_id = request.POST.get('aluno')
        conceito_id = request.POST.get('conceito')
        observacoes = request.POST.get('observacoes', '')
        
        if turma_id and disciplina_id and aluno_id and conceito_id:
            from alunos.models import Aluno
            turma = get_object_or_404(Turma, id=turma_id)
            disciplina = get_object_or_404(Disciplina, id=disciplina_id)
            aluno = get_object_or_404(Aluno, id=aluno_id)
            conceito = get_object_or_404(Conceito, id=conceito_id)
            
            LancamentoNota.objects.create(
                turma=turma,
                disciplina=disciplina,
                aluno=aluno,
                conceito=conceito,
                observacoes=observacoes,
                usuario_lancamento=request.user
            )
            messages.success(request, 'Nota lançada com sucesso!')
            return redirect('avaliacao:notas_list')
    
    context = {
        'turmas': turmas,
        'disciplinas': disciplinas,
        'conceitos': conceitos,
    }
    
    return render(request, 'avaliacao/lancar_notas.html', context)


@login_required
def conceitos_list(request):
    """
    Lista todos os conceitos
    """
    conceitos = Conceito.objects.all().order_by('valor')
    
    context = {
        'conceitos': conceitos,
    }
    
    return render(request, 'avaliacao/conceitos_list.html', context)


@login_required
def relatorios(request):
    """
    Página de relatórios de avaliação
    """
    # Estatísticas para relatórios
    stats = {
        'total_alunos_avaliados': LancamentoNota.objects.values('aluno').distinct().count(),
        'media_geral': LancamentoNota.objects.aggregate(
            avg_valor=Avg('conceito__valor')
        )['avg_valor'] or 0,
        'total_recuperacoes': RecuperacaoEspecial.objects.count(),
        'total_atestados': AtestadoMedico.objects.count(),
    }
    
    context = {
        'stats': stats,
    }
    
    return render(request, 'avaliacao/relatorios.html', context)


@login_required
def diario_online(request):
    """
    Diário online para registro de conteúdos e frequência
    """
    turmas = Turma.objects.all()
    
    # Conteúdos recentes
    conteudos_recentes = ConteudoAula.objects.order_by('-data_aula')[:10]
    
    if request.method == 'POST':
        turma_id = request.POST.get('turma')
        disciplina_id = request.POST.get('disciplina')
        data_aula = request.POST.get('data_aula')
        conteudo = request.POST.get('conteudo')
        
        if turma_id and disciplina_id and data_aula and conteudo:
            turma = get_object_or_404(Turma, id=turma_id)
            disciplina = get_object_or_404(Disciplina, id=disciplina_id)
            
            ConteudoAula.objects.create(
                turma=turma,
                disciplina=disciplina,
                data_aula=data_aula,
                conteudo=conteudo,
                usuario_registro=request.user
            )
            messages.success(request, 'Conteúdo registrado com sucesso!')
            return redirect('avaliacao:diario_online')
    
    context = {
        'turmas': turmas,
        'conteudos_recentes': conteudos_recentes,
    }
    
    return render(request, 'avaliacao/diario_online.html', context)


@login_required
def enturmar_alunos(request, pk):
    """
    View para enturmar alunos em uma turma
    """
    turma = get_object_or_404(Turma, pk=pk)
    
    # Alunos disponíveis (não enturmados nesta turma)
    alunos_enturmados_ids = Enturmacao.objects.filter(
        turma=turma, ativo=True
    ).values_list('aluno', flat=True)
    
    alunos_disponiveis = Aluno.objects.exclude(
        codigo__in=alunos_enturmados_ids
    ).order_by('nome')
    
    if request.method == 'POST':
        alunos_selecionados = request.POST.getlist('alunos')
        
        if alunos_selecionados:
            # Verificar se ainda há vagas
            vagas_restantes = turma.get_vagas_disponiveis()
            
            if len(alunos_selecionados) > vagas_restantes:
                messages.error(
                    request, 
                    f'Você selecionou {len(alunos_selecionados)} alunos, mas há apenas {vagas_restantes} vagas disponíveis.'
                )
                return redirect('avaliacao:enturmar_alunos', pk=pk)
            
            # Enturmar os alunos selecionados
            for aluno_codigo in alunos_selecionados:
                aluno = get_object_or_404(Aluno, codigo=aluno_codigo)
                
                Enturmacao.objects.create(
                    turma=turma,
                    aluno=aluno,
                    usuario_enturmacao=request.user
                )
            
            # Registrar atividade
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='ENTURMAR',
                modulo='AVALIACAO',
                objeto_nome=turma.nome,
                objeto_id=turma.id,
                descricao=f'{len(alunos_selecionados)} aluno(s) enturmado(s) em {turma.nome}'
            )
            
            messages.success(
                request, 
                f'{len(alunos_selecionados)} aluno(s) enturmado(s) com sucesso!'
            )
            return redirect('avaliacao:turma_detail', pk=pk)
        else:
            messages.warning(request, 'Nenhum aluno foi selecionado.')
    
    context = {
        'turma': turma,
        'alunos_disponiveis': alunos_disponiveis,
        'vagas_disponiveis': turma.get_vagas_disponiveis(),
    }
    
    return render(request, 'avaliacao/enturmar_alunos.html', context)


@login_required 
def desenturmar_aluno(request, pk, aluno_id):
    """
    View para desenturmar um aluno de uma turma
    """
    turma = get_object_or_404(Turma, pk=pk)
    aluno = get_object_or_404(Aluno, codigo=aluno_id)
    
    # Buscar a enturmação ativa
    enturmacao = get_object_or_404(
        Enturmacao, 
        turma=turma, 
        aluno=aluno, 
        ativo=True
    )
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        
        # Desenturmar o aluno
        enturmacao.ativo = False
        enturmacao.data_desenturmacao = date.today()
        enturmacao.motivo_desenturmacao = motivo
        enturmacao.usuario_desenturmacao = request.user
        enturmacao.save()
        
        # Registrar atividade
        AtividadeRecente.registrar_atividade(
            usuario=request.user,
            acao='DESENTURMAR',
            modulo='AVALIACAO',
            objeto_nome=turma.nome,
            objeto_id=turma.id,
            descricao=f'{aluno.nome} desenturmado(a) de {turma.nome}'
        )
        
        messages.success(request, f'{aluno.nome} foi desenturmado(a) com sucesso!')
        return redirect('avaliacao:turma_detail', pk=pk)
    
    context = {
        'turma': turma,
        'aluno': aluno,
        'enturmacao': enturmacao,
    }
    
    return render(request, 'avaliacao/confirmar_desenturmacao.html', context)