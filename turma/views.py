from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Avg, Q
from django.db import models
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import date, datetime
from .models import (
    Conceito, Turma, Disciplina, LancamentoNota, PendenciaAvaliacao,
    Enturmacao, AulaRegistrada, RegistroFrequencia,
    TipoAvaliacao, Avaliacao,
    NotaAvaliacao, DivisaoPeriodoLetivo
)
from diario.models import DiarioEletronico
from .forms import TurmaForm, DisciplinaForm, AvaliacaoForm, DivisaoPeriodoLetivoForm
from . import relatorios as relatorios_turma
from alunos.models import Aluno
from dashboard.models import AtividadeRecente


@login_required
def avaliacao_home(request):
    """Dashboard principal do módulo Avaliação"""
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
    
    return render(request, 'turma/home.html', context)


@login_required
def turmas_list(request):
    """Lista todas as turmas com filtros"""
    turmas = Turma.objects.all().order_by('nome')
    
    # Filtros
    tipo_ensino = request.GET.get('tipo_ensino')
    ano_serie = request.GET.get('ano_serie')
    turno = request.GET.get('turno')
    
    if tipo_ensino:
        turmas = turmas.filter(tipo_ensino=tipo_ensino)
    if ano_serie:
        turmas = turmas.filter(ano_serie=ano_serie)
    if turno:
        turmas = turmas.filter(turno=turno)
    
    # Forçar recalculo dos dados das turmas para evitar cache
    for turma in turmas:
        # Força recálculo dos métodos para cada turma
        turma._prefetched_objects_cache = {}
    
    paginator = Paginator(turmas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calcular estatísticas atualizadas
    total_turmas = turmas.count()
    total_alunos_enturmados = sum([turma.get_total_alunos() for turma in turmas])
    total_vagas = sum([turma.vagas_total for turma in turmas])
    vagas_ocupadas = total_alunos_enturmados
    vagas_disponiveis = total_vagas - vagas_ocupadas
    
    context = {
        'page_obj': page_obj,
        'turmas': page_obj,
        'total_turmas': total_turmas,
        'total_alunos_enturmados': total_alunos_enturmados,
        'total_vagas': total_vagas,
        'vagas_ocupadas': vagas_ocupadas,
        'vagas_disponiveis': vagas_disponiveis,
        'current_filters': {
            'tipo_ensino': tipo_ensino,
            'ano_serie': ano_serie,
            'turno': turno,
        }
    }
    return render(request, 'turma/turmas_list.html', context)


@login_required
def turma_create(request):
    """Cria uma nova turma"""
    # Capturar a página de origem para voltar corretamente
    next_url = request.GET.get('next', 'turma:turmas_list')
    
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            turma = form.save()
            messages.success(request, f'Turma "{turma.nome}" criada com sucesso!')
            
            # Registrar atividade
            AtividadeRecente.objects.create(
                usuario=request.user,
                acao='CRIAR',
                modulo='AVALIACAO',
                objeto_nome=turma.nome,
                descricao=f'Criou a turma {turma.nome}'
            )
            
            # Verificar se veio do diário home para redirecionar corretamente
            if 'diario' in request.POST.get('next', ''):
                return redirect('diario:home')
            return redirect('turma:turmas_list')
    else:
        form = TurmaForm()
    
    context = {
        'form': form,
        'next_url': next_url,
        'is_create': True,
        'title': 'Criar Nova Turma'
    }
    
    return render(request, 'turma/turma_form.html', context)


@login_required
def turma_edit(request, pk):
    """Edita uma turma existente"""
    turma = get_object_or_404(Turma, pk=pk)
    
    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma)
        if form.is_valid():
            form.save()
            messages.success(request, f'Turma "{turma.nome}" editada com sucesso!')
            
            # Registrar atividade
            AtividadeRecente.objects.create(
                usuario=request.user,
                acao='EDITAR',
                modulo='AVALIACAO',
                objeto_nome=turma.nome,
                descricao=f'Editou a turma {turma.nome}'
            )
            
            return redirect('turma:turmas_list')
    else:
        form = TurmaForm(instance=turma)
    
    return render(request, 'turma/turma_form.html', {'form': form, 'turma': turma})


@login_required
def turma_detail(request, pk):
    """Detalhe de uma turma"""
    turma = get_object_or_404(Turma, pk=pk)
    alunos_enturmados = turma.get_alunos_enturmados()
    avaliacoes = Avaliacao.objects.filter(turma=turma).order_by('-data_aplicacao')[:5]

    # Verificar se veio do diário
    from_diary = request.GET.get('from_diary') == 'true'

    context = {
        'turma': turma,
        'alunos_enturmados': alunos_enturmados,
        'avaliacoes': avaliacoes,
        'total_alunos': alunos_enturmados.count(),
        'from_diary': from_diary,
    }
    return render(request, 'turma/turma_detail.html', context)


@login_required
def turma_delete(request, pk):
    """Exclui uma turma"""
    turma = get_object_or_404(Turma, pk=pk)
    
    if request.method == 'POST':
        nome_turma = turma.nome
        turma.delete()
        messages.success(request, f'Turma "{nome_turma}" excluída com sucesso!')
        
        # Registrar atividade
        AtividadeRecente.objects.create(
            usuario=request.user,
            acao='DELETAR',
            modulo='AVALIACAO',
            objeto_nome=nome_turma,
            descricao=f'Excluiu a turma {nome_turma}'
        )
        
        return redirect('turma:turmas_list')
    
    return render(request, 'turma/turma_confirm_delete.html', {'turma': turma})


@login_required
def disciplinas_list(request):
    """Lista todas as disciplinas"""
    disciplinas = Disciplina.objects.all().order_by('nome')
    
    paginator = Paginator(disciplinas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'disciplinas': page_obj,
    }
    return render(request, 'turma/disciplinas_list.html', context)


@login_required
def disciplina_create(request):
    """Cria uma nova disciplina"""
    if request.method == 'POST':
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            disciplina = form.save()
            messages.success(request, f'Disciplina "{disciplina.nome}" criada com sucesso!')
            
            # Registrar atividade
            AtividadeRecente.objects.create(
                usuario=request.user,
                acao='CRIAR',
                modulo='AVALIACAO',
                objeto_nome=disciplina.nome,
                descricao=f'Criou a disciplina {disciplina.nome}'
            )
            
            return redirect('turma:disciplinas_list')
    else:
        form = DisciplinaForm()
    
    return render(request, 'turma/disciplina_form.html', {'form': form})


@login_required
def disciplina_edit(request, pk):
    """Edita uma disciplina existente"""
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    if request.method == 'POST':
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            form.save()
            messages.success(request, f'Disciplina "{disciplina.nome}" editada com sucesso!')
            
            # Registrar atividade
            AtividadeRecente.objects.create(
                usuario=request.user,
                acao='EDITAR',
                modulo='AVALIACAO',
                objeto_nome=disciplina.nome,
                descricao=f'Editou a disciplina {disciplina.nome}'
            )
            
            return redirect('turma:disciplinas_list')
    else:
        form = DisciplinaForm(instance=disciplina)
    
    return render(request, 'turma/disciplina_form.html', {'form': form, 'disciplina': disciplina})


@login_required
def disciplina_delete(request, pk):
    """Exclui uma disciplina"""
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    if request.method == 'POST':
        nome_disciplina = disciplina.nome
        disciplina.delete()
        messages.success(request, f'Disciplina "{nome_disciplina}" excluída com sucesso!')
        
        # Registrar atividade
        AtividadeRecente.objects.create(
            usuario=request.user,
            acao='DELETAR',
            modulo='AVALIACAO',
            objeto_nome=nome_disciplina,
            descricao=f'Excluiu a disciplina {nome_disciplina}'
        )
        
        return redirect('turma:disciplinas_list')
    
    return render(request, 'turma/disciplina_confirm_delete.html', {'disciplina': disciplina})


@login_required
def notas_list(request):
    """Lista os lançamentos de notas"""
    lancamentos = LancamentoNota.objects.all().order_by('-data_lancamento')
    
    # Filtros
    turma_id = request.GET.get('turma')
    disciplina_id = request.GET.get('disciplina')
    
    if turma_id:
        lancamentos = lancamentos.filter(turma_id=turma_id)
    if disciplina_id:
        lancamentos = lancamentos.filter(disciplina_id=disciplina_id)
    
    paginator = Paginator(lancamentos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    turmas = Turma.objects.all().order_by('nome')
    disciplinas = Disciplina.objects.all().order_by('nome')
    
    context = {
        'page_obj': page_obj,
        'lancamentos': page_obj,
        'turmas': turmas,
        'disciplinas': disciplinas,
        'current_filters': {
            'turma': turma_id,
            'disciplina': disciplina_id,
        }
    }
    return render(request, 'turma/notas_list.html', context)


@login_required
def lancar_notas(request):
    """Seleção da avaliação para lançamento de notas (com filtros por turma e disciplina)"""
    turma_id = request.GET.get('turma', '')
    disciplina_id = request.GET.get('disciplina', '')

    avaliacoes = Avaliacao.objects.filter(ativo=True).select_related(
        'turma', 'disciplina', 'tipo_avaliacao', 'divisao_periodo'
    ).order_by('-data_aplicacao')
    if turma_id:
        avaliacoes = avaliacoes.filter(turma_id=turma_id)
    if disciplina_id:
        avaliacoes = avaliacoes.filter(disciplina_id=disciplina_id)

    context = {
        'avaliacoes': avaliacoes,
        'turmas': Turma.objects.order_by('nome'),
        'disciplinas': Disciplina.objects.filter(ativo=True).order_by('nome'),
        'turma_selecionada': turma_id,
        'disciplina_selecionada': disciplina_id,
    }
    return render(request, 'turma/lancar_notas.html', context)


@login_required
def avaliacao_create(request):
    """Cria uma nova avaliação (visão da coordenação)"""
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, user=request.user)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.professor = request.user
            avaliacao.save()
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='CRIAR',
                modulo='AVALIACAO',
                objeto_nome=avaliacao.nome,
                objeto_id=avaliacao.pk,
                descricao=f'Criou a avaliação {avaliacao.nome} para a turma {avaliacao.turma.nome}'
            )
            messages.success(request, f'Avaliação "{avaliacao.nome}" criada com sucesso!')
            return redirect('turma:avaliacao_detail', pk=avaliacao.pk)
    else:
        form = AvaliacaoForm(user=request.user, initial={
            'data_aplicacao': date.today(),
            'turma': request.GET.get('turma'),
            'disciplina': request.GET.get('disciplina'),
        })

    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Nova Avaliação',
        'subtitle': 'Cadastre uma avaliação para uma turma, disciplina e período',
        'icon': 'fa-clipboard-check',
        'cancel_url': reverse('turma:avaliacoes_list'),
        'submit_label': 'Criar avaliação',
    })


@login_required
def conceitos_list(request):
    """Lista os conceitos disponíveis"""
    conceitos = Conceito.objects.all()
    
    context = {
        'conceitos': conceitos
    }
    return render(request, 'turma/conceitos_list.html', context)


@login_required
def relatorios(request):
    """Central de relatórios das turmas: boletins, frequência e desempenho"""
    turmas = Turma.objects.annotate(
        total_alunos=Count('enturmacoes', filter=Q(enturmacoes__ativo=True))
    ).order_by('-periodo_letivo', 'nome')
    turma = None
    alunos = []
    turma_id = request.GET.get('turma')
    if turma_id:
        turma = get_object_or_404(Turma, pk=turma_id)
        alunos = turma.get_alunos_enturmados()
    return render(request, 'turma/relatorios.html', {'turmas': turmas, 'turma': turma, 'alunos': alunos})


@login_required
def divisoes(request):
    """Cadastro das divisões do período letivo (bimestres, trimestres...) usadas pelo diário"""
    periodo = request.GET.get('periodo') or str(date.today().year)
    form = DivisaoPeriodoLetivoForm(request.POST or None, initial={
        'periodo_letivo': periodo, 'tipo_divisao': 'BIMESTRE',
        'ordem': DivisaoPeriodoLetivo.objects.filter(periodo_letivo=periodo).count() + 1,
    })

    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'gerar_bimestres':
            ano = int(request.POST.get('ano') or periodo)
            if DivisaoPeriodoLetivo.objects.filter(periodo_letivo=str(ano)).exists():
                messages.error(request, f'Já existem divisões cadastradas para {ano}.')
            else:
                limites = [((2, 1), (4, 15)), ((4, 16), (6, 30)), ((8, 1), (9, 30)), ((10, 1), (12, 15))]
                for ordem, (inicio, fim) in enumerate(limites, start=1):
                    DivisaoPeriodoLetivo.objects.create(
                        nome=f'{ordem}º Bimestre', tipo_divisao='BIMESTRE', periodo_letivo=str(ano), ordem=ordem,
                        data_inicio=date(ano, *inicio), data_fim=date(ano, *fim),
                    )
                messages.success(request, f'4 bimestres criados para {ano}. Ajuste as datas se necessário.')
            return redirect(f"{reverse('turma:divisoes')}?periodo={ano}")
        if acao == 'alternar':
            divisao = get_object_or_404(DivisaoPeriodoLetivo, pk=request.POST.get('divisao'))
            divisao.ativo = not divisao.ativo
            divisao.save(update_fields=['ativo'])
            messages.success(request, f'{divisao.nome} {"ativada" if divisao.ativo else "desativada"}.')
            return redirect(f"{reverse('turma:divisoes')}?periodo={divisao.periodo_letivo}")
        if form.is_valid():
            divisao = form.save()
            messages.success(request, f'{divisao.nome} cadastrado com sucesso.')
            return redirect(f"{reverse('turma:divisoes')}?periodo={divisao.periodo_letivo}")

    anos = sorted(
        set(DivisaoPeriodoLetivo.objects.values_list('periodo_letivo', flat=True))
        | set(Turma.objects.values_list('periodo_letivo', flat=True)) | {periodo},
        reverse=True,
    )
    context = {
        'form': form,
        'periodo': periodo,
        'anos': anos,
        'divisoes': DivisaoPeriodoLetivo.objects.filter(periodo_letivo=periodo).annotate(
            total_avaliacoes=Count('avaliacao')
        ).order_by('ordem'),
    }
    return render(request, 'turma/divisoes.html', context)


@login_required
def boletim_aluno(request, turma_id, aluno_id):
    """Boletim escolar do aluno na turma"""
    turma = get_object_or_404(Turma, pk=turma_id)
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    if not Enturmacao.objects.filter(turma=turma, aluno=aluno).exists():
        messages.error(request, 'O aluno não pertence a esta turma.')
        return redirect(f"{reverse('turma:relatorios')}?turma={turma.pk}")
    context = {'turma': turma, 'aluno': aluno, **relatorios_turma.calcular_boletim(turma, aluno)}
    return render(request, 'turma/boletim_aluno.html', context)


@login_required
def relatorio_frequencia(request, turma_id):
    """Frequência dos alunos da turma por disciplina"""
    turma = get_object_or_404(Turma, pk=turma_id)
    alunos = list(turma.get_alunos_enturmados())
    context = {'turma': turma, **relatorios_turma.calcular_frequencia_turma(turma, alunos)}
    return render(request, 'turma/relatorio_frequencia.html', context)


@login_required
def relatorio_desempenho(request, turma_id):
    """Desempenho da turma: médias por disciplina e distribuição dos alunos"""
    turma = get_object_or_404(Turma, pk=turma_id)
    alunos = list(turma.get_alunos_enturmados())
    context = {'turma': turma, 'total_alunos': len(alunos),
               **relatorios_turma.calcular_desempenho_turma(turma, alunos)}
    return render(request, 'turma/relatorio_desempenho.html', context)


@login_required
def enturmar_alunos(request, pk):
    """Enturma alunos em uma turma específica"""
    turma = get_object_or_404(Turma, pk=pk)
    
    if request.method == 'POST':
        alunos_ids = request.POST.getlist('alunos')
        confirmar_transferencia = request.POST.get('confirmar_transferencia')
        
        # Primeira passagem: verificar se há alunos já enturmados
        alunos_ja_enturmados = []
        for aluno_id in alunos_ids:
            aluno = get_object_or_404(Aluno, codigo=aluno_id)
            enturmacao_existente = Enturmacao.objects.filter(aluno=aluno, ativo=True).first()
            if enturmacao_existente:
                alunos_ja_enturmados.append({
                    'aluno': aluno,
                    'turma_atual': enturmacao_existente.turma
                })
        
        # Se há alunos já enturmados e não foi confirmado, mostrar confirmação
        if alunos_ja_enturmados and not confirmar_transferencia:
            # Verificar se veio do diário
            from_diary = request.POST.get('from_diary') or request.GET.get('from_diary') == 'true'
            context = {
                'turma': turma,
                'alunos_ja_enturmados': alunos_ja_enturmados,
                'alunos_ids': alunos_ids,
                'mostrar_confirmacao': True,
                'from_diary': from_diary,
            }
            return render(request, 'turma/enturmar_alunos.html', context)
        
        # Processar enturmações (normal ou com confirmação)
        for aluno_id in alunos_ids:
            aluno = get_object_or_404(Aluno, codigo=aluno_id)
            
            # Verificar se o aluno já está enturmado em QUALQUER turma ativa
            if not Enturmacao.objects.filter(aluno=aluno, ativo=True).exists():
                Enturmacao.objects.create(
                    turma=turma,
                    aluno=aluno,
                    data_enturmacao=date.today(),
                    ativo=True,
                    usuario_enturmacao=request.user
                )
            else:
                # Se aluno já está em outra turma, desenturmar da anterior
                enturmacao_anterior = Enturmacao.objects.get(aluno=aluno, ativo=True)
                
                # Verificar se já existe enturmação inativa para este aluno
                if Enturmacao.objects.filter(aluno=aluno, ativo=False).exists():
                    # Se já existe, deletar a enturmação anterior em vez de desativar
                    enturmacao_anterior.delete()
                else:
                    # Se não existe, pode desativar normalmente
                    enturmacao_anterior.ativo = False
                    enturmacao_anterior.data_desenturmacao = date.today()
                    enturmacao_anterior.motivo_desenturmacao = f"Transferido para {turma.nome}"
                    enturmacao_anterior.usuario_desenturmacao = request.user
                    enturmacao_anterior.save()
                
                # Criar nova enturmação
                Enturmacao.objects.create(
                    turma=turma,
                    aluno=aluno,
                    data_enturmacao=date.today(),
                    ativo=True,
                    usuario_enturmacao=request.user
                )
        
        messages.success(request, f'{len(alunos_ids)} aluno(s) enturmado(s) com sucesso!')
        return redirect('turma:turma_detail', pk=pk)
    
    # Alunos já enturmados nesta turma
    alunos_enturmados_ids = Enturmacao.objects.filter(
        turma=turma, 
        ativo=True
    ).values_list('aluno__codigo', flat=True)
    
    # Alunos disponíveis para enturmar
    alunos_disponiveis = Aluno.objects.exclude(
        codigo__in=alunos_enturmados_ids
    ).order_by('nome')
    
    # Calcular vagas disponíveis
    vagas_disponiveis = turma.get_vagas_disponiveis()

    # Verificar se veio do diário
    from_diary = request.GET.get('from_diary') == 'true'

    context = {
        'turma': turma,
        'alunos_disponiveis': alunos_disponiveis,
        'vagas_disponiveis': vagas_disponiveis,
        'from_diary': from_diary,
    }
    return render(request, 'turma/enturmar_alunos.html', context)


@login_required
def desenturmar_aluno(request, pk, aluno_id):
    """Remove um aluno de uma turma"""
    turma = get_object_or_404(Turma, pk=pk)
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    
    if request.method == 'POST':
        enturmacao = get_object_or_404(
            Enturmacao, 
            turma=turma, 
            aluno=aluno, 
            ativo=True
        )
        
        # Verificar se já existe enturmação inativa para este aluno
        if Enturmacao.objects.filter(aluno=aluno, ativo=False).exists():
            # Se já existe, deletar esta enturmação em vez de desativar
            enturmacao.delete()
        else:
            # Se não existe, pode desativar normalmente
            enturmacao.ativo = False
            enturmacao.data_desenturmacao = date.today()
            enturmacao.usuario_desenturmacao = request.user
            enturmacao.save()
        
        messages.success(request, f'Aluno {aluno.nome} desenturmado da turma {turma.nome}!')
        return redirect('turma:turma_detail', pk=turma.pk)
    
    context = {
        'turma': turma,
        'aluno': aluno,
    }
    return render(request, 'turma/desenturmar_aluno.html', context)


@login_required
def gerenciar_disciplinas_turma(request, turma_id):
    """Gerencia as disciplinas de uma turma"""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    if request.method == 'POST':
        disciplinas_ids = request.POST.getlist('disciplinas')
        selecionadas = Disciplina.objects.filter(pk__in=disciplinas_ids)

        # Diários das disciplinas desmarcadas são desativados (o histórico é preservado)
        DiarioEletronico.objects.filter(turma=turma).exclude(disciplina__in=selecionadas).update(ativo=False)
        for disciplina in selecionadas:
            DiarioEletronico.objects.update_or_create(
                turma=turma,
                disciplina=disciplina,
                defaults={'periodo_letivo': turma.periodo_letivo, 'ativo': True},
            )
        
        messages.success(request, f'{len(disciplinas_ids)} disciplina(s) vinculada(s) à turma com sucesso!')
        return redirect('turma:turma_detail', pk=turma_id)
    
    todas_disciplinas = Disciplina.objects.all().order_by('nome')
    # Buscar disciplinas que têm diários para esta turma
    disciplinas_turma = Disciplina.objects.filter(
        diarioeletronico__turma=turma, diarioeletronico__ativo=True
    ).distinct().order_by('nome')
    
    context = {
        'turma': turma,
        'todas_disciplinas': todas_disciplinas,
        'disciplinas_turma': disciplinas_turma,
    }
    return render(request, 'turma/gerenciar_disciplinas_turma.html', context)


@login_required
def avaliacoes_list(request):
    """Lista todas as avaliações"""
    avaliacoes = Avaliacao.objects.all().order_by('-data_aplicacao')
    
    # Filtros
    turma_id = request.GET.get('turma')
    disciplina_id = request.GET.get('disciplina')
    tipo_id = request.GET.get('tipo')
    status = request.GET.get('status')
    
    if turma_id:
        avaliacoes = avaliacoes.filter(turma_id=turma_id)
    if disciplina_id:
        avaliacoes = avaliacoes.filter(disciplina_id=disciplina_id)
    if tipo_id:
        avaliacoes = avaliacoes.filter(tipo_avaliacao_id=tipo_id)
    hoje = date.today()
    if status == 'agendada':
        avaliacoes = avaliacoes.filter(data_aplicacao__gt=hoje)
    elif status == 'em_andamento':
        avaliacoes = avaliacoes.filter(data_aplicacao=hoje)
    elif status == 'finalizada':
        avaliacoes = avaliacoes.filter(data_aplicacao__lt=hoje)
    avaliacoes = avaliacoes.select_related('turma', 'disciplina', 'tipo_avaliacao', 'divisao_periodo')

    paginator = Paginator(avaliacoes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    turmas = Turma.objects.all().order_by('nome')
    disciplinas = Disciplina.objects.all().order_by('nome')
    tipos = TipoAvaliacao.objects.all().order_by('nome')
    
    context = {
        'page_obj': page_obj,
        'avaliacoes': page_obj,
        'turmas': turmas,
        'disciplinas': disciplinas,
        'tipos': tipos,
        'hoje': hoje,
        'current_filters': {
            'turma': turma_id,
            'disciplina': disciplina_id,
            'tipo': tipo_id,
            'status': status,
        }
    }
    return render(request, 'turma/avaliacoes_list.html', context)


@login_required
def avaliacao_detail(request, pk):
    """Detalhe de uma avaliação com as notas lançadas"""
    avaliacao = get_object_or_404(
        Avaliacao.objects.select_related('turma', 'disciplina', 'divisao_periodo', 'tipo_avaliacao', 'professor'),
        pk=pk
    )
    notas = avaliacao.notas.select_related('aluno', 'conceito').order_by('aluno__nome')
    estatisticas = notas.filter(nota__isnull=False).aggregate(
        media=Avg('nota'), maior_nota=models.Max('nota'), menor_nota=models.Min('nota')
    )
    estatisticas['total_notas'] = notas.count()
    estatisticas['total_alunos'] = avaliacao.turma.enturmacoes.filter(ativo=True).count()

    context = {
        'avaliacao': avaliacao,
        'notas': notas,
        'estatisticas': estatisticas,
    }
    return render(request, 'turma/avaliacao_detail.html', context)


@login_required
def avaliacao_edit(request, pk):
    """A edição de avaliações é feita pelo diário eletrônico"""
    return redirect('turma:editar_avaliacao_diario', avaliacao_id=pk)


@login_required
def avaliacao_delete(request, pk):
    """Exclui uma avaliação"""
    avaliacao = get_object_or_404(Avaliacao, pk=pk)

    if request.method == 'POST' and request.POST.get('confirmar') == 'sim':
        nome_avaliacao = avaliacao.nome
        avaliacao.delete()
        AtividadeRecente.registrar_atividade(
            usuario=request.user,
            acao='DELETAR',
            modulo='AVALIACAO',
            objeto_nome=nome_avaliacao,
            descricao=f'Excluiu a avaliação {nome_avaliacao}'
        )
        messages.success(request, f'Avaliação "{nome_avaliacao}" excluída com sucesso!')
        return redirect('turma:avaliacoes_list')

    return render(request, 'generic/confirm_delete.html', {
        'title': 'Excluir Avaliação',
        'object_label': avaliacao.nome,
        'cancel_url': reverse('turma:avaliacao_detail', args=[avaliacao.pk]),
        'details': [
            f'Turma: {avaliacao.turma.nome}',
            f'Disciplina: {avaliacao.disciplina.nome}',
            f'{avaliacao.notas.count()} nota(s) lançada(s) também serão excluídas.',
        ],
    })


@login_required
def get_anos_series_por_tipo(request):
    """AJAX endpoint para obter anos/séries por tipo de ensino"""
    tipo_ensino = request.GET.get('tipo_ensino')
    
    if not tipo_ensino:
        return JsonResponse({'anos_series': []})
    
    # Usar o método do modelo para obter as opções
    turma_temp = Turma()
    anos_series = turma_temp.get_anos_series_por_tipo(tipo_ensino)
    
    return JsonResponse({'anos_series': anos_series})


# ==========================================
# DIÁRIO ELETRÔNICO - NOVAS FUNCIONALIDADES
# ==========================================

@login_required
def fazer_chamada(request, turma_id):
    """Interface para fazer chamada de presença"""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Obter disciplina da URL
    disciplina_id = request.GET.get('disciplina')
    if not disciplina_id:
        # Redirecionar para seleção de disciplina
        messages.error(request, 'Selecione uma disciplina para fazer a chamada.')
        return redirect('diario:turma', turma_id=turma_id)

    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)

    # Obter divisão (bimestre/período) da URL
    divisao_id = request.GET.get('divisao')
    if not divisao_id:
        messages.info(request, 'Selecione o período (bimestre/trimestre) para continuar.')
        return redirect('diario:disciplina', turma_id=turma.pk, disciplina_id=disciplina.pk)
    divisao = get_object_or_404(DivisaoPeriodoLetivo, pk=divisao_id)

    # Buscar alunos da turma
    alunos = Aluno.objects.filter(
        enturmacoes__turma=turma,
        enturmacoes__ativo=True
    ).order_by('nome')
    
    # Obter data da chamada (URL param ou hoje)
    data_param = request.GET.get('data')
    if data_param:
        try:
            data_chamada = datetime.strptime(data_param, '%Y-%m-%d').date()
        except ValueError:
            data_chamada = date.today()
    else:
        data_chamada = date.today()
    
    # Buscar aula da data específica para carregar status da chamada
    aula_data = AulaRegistrada.objects.filter(
        turma=turma,
        disciplina=disciplina,
        data_aula=data_chamada
    ).first()
    
    # Carregar registros de frequência existentes
    registros_freq = {}
    if aula_data:
        registros = RegistroFrequencia.objects.filter(aula=aula_data)
        for registro in registros:
            registros_freq[registro.aluno.codigo] = registro.situacao
    
    # Adicionar status atual aos alunos
    alunos_list = list(alunos)
    for aluno in alunos_list:
        aluno.status_atual = registros_freq.get(aluno.codigo, 'PRESENTE')
    
    if request.method == 'POST':
        # Processar dados da chamada
        data_aula = request.POST.get('data_aula', date.today().strftime('%Y-%m-%d'))
        
        # Debug: verificar dados recebidos
        print(f"POST data: {request.POST}")
        for key, value in request.POST.items():
            if key.startswith('toggle_'):
                print(f"{key}: {value}")
        
        # Primeiro, criar ou buscar uma aula para hoje
        try:
            aula, aula_created = AulaRegistrada.objects.get_or_create(
                turma=turma,
                disciplina=disciplina,
                data_aula=data_aula,
                professor=request.user,
                defaults={
                    'horario_inicio': '08:00',
                    'horario_fim': '12:00', 
                    'conteudo_programatico': f'Registro de frequência - {date.today().strftime("%d/%m/%Y")}',
                    'observacoes': 'Aula criada automaticamente pelo sistema de chamada eletrônica',
                    'chamada_realizada': True
                }
            )
        except Exception as e:
            messages.error(request, f'Erro ao criar aula: {str(e)}')
            return redirect('diario:divisao', turma_id=turma.pk, disciplina_id=disciplina.pk, divisao_id=divisao.pk)
        
        for aluno in alunos:
            # Novo sistema de toggle - o JavaScript envia o status do toggle
            status_toggle = request.POST.get(f'toggle_{aluno.codigo}', 'presente')
            presente = status_toggle == 'presente'
            
            # Registrar ou atualizar presença
            registro, created = RegistroFrequencia.objects.get_or_create(
                aula=aula,  # Agora incluindo a aula obrigatória
                aluno=aluno,
                defaults={
                    'situacao': 'PRESENTE' if presente else 'AUSENTE',
                    'usuario_registro': request.user
                }
            )
            
            if not created:
                registro.situacao = 'PRESENTE' if presente else 'AUSENTE'
                registro.save()
        
        messages.success(request, f'Chamada do dia {date.today().strftime("%d/%m/%Y")} registrada com sucesso!')
        return redirect('diario:disciplina', turma_id=turma_id, disciplina_id=disciplina.pk)
    
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisao': divisao,
        'alunos': alunos_list,  # Usar lista com status
        'data_hoje': date.today(),
        'data_atual': data_chamada.strftime('%Y-%m-%d'),  # Data para o input
        'page_title': f'Chamada - {disciplina.nome} - {turma.nome}'
    }
    
    return render(request, 'diario/fazer_chamada_diario.html', context)


@login_required
def lancar_notas_diario(request, turma_id):
    """Interface para lançar notas no diário"""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Obter disciplina da URL
    disciplina_id = request.GET.get('disciplina')
    if not disciplina_id:
        messages.error(request, 'Selecione uma disciplina para lançar notas.')
        return redirect('diario:turma', turma_id=turma_id)

    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)

    # Obter divisão (bimestre/período) da URL
    divisao_id = request.GET.get('divisao')
    if not divisao_id:
        messages.info(request, 'Selecione o período (bimestre/trimestre) para continuar.')
        return redirect('diario:disciplina', turma_id=turma.pk, disciplina_id=disciplina.pk)
    divisao = get_object_or_404(DivisaoPeriodoLetivo, pk=divisao_id)

    # Buscar alunos da turma
    alunos = Aluno.objects.filter(
        enturmacoes__turma=turma,
        enturmacoes__ativo=True
    ).order_by('nome')

    # Buscar avaliações da turma e disciplina
    avaliacoes = Avaliacao.objects.filter(
        turma=turma,
        disciplina=disciplina
    ).order_by('nome')
    
    # Buscar notas existentes da disciplina
    notas_existentes = NotaAvaliacao.objects.filter(
        avaliacao__turma=turma,
        avaliacao__disciplina=disciplina,
        aluno__in=alunos
    ).select_related('avaliacao', 'aluno')
    
    # Adicionar notas aos alunos
    alunos_list = list(alunos)
    notas_dict = {}
    for nota in notas_existentes:
        if nota.aluno.codigo not in notas_dict:
            notas_dict[nota.aluno.codigo] = []
        notas_dict[nota.aluno.codigo].append(nota)
    
    # Adicionar as notas como atributo aos alunos
    for aluno in alunos_list:
        aluno.notas_existentes = notas_dict.get(aluno.codigo, [])
    
    # Handle AJAX request for saving grades
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        import json
        try:
            data = json.loads(request.body)
            aluno_id = data.get('aluno_id')
            avaliacao_id = data.get('avaliacao_id')
            nota_valor = data.get('nota')
            
            aluno = get_object_or_404(Aluno, codigo=aluno_id)  # Aluno usa 'codigo' como PK
            avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
            
            # Criar ou atualizar a nota
            nota_obj, created = NotaAvaliacao.objects.get_or_create(
                aluno=aluno,
                avaliacao=avaliacao,
                defaults={
                    'nota': nota_valor,
                    'usuario_lancamento': request.user
                }
            )
            
            if not created:
                nota_obj.nota = nota_valor
                nota_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Nota {nota_valor} salva com sucesso!',
                'nota': float(nota_valor) if nota_valor else None
            })
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Erro ao salvar nota: {error_detail}")
            return JsonResponse({
                'success': False,
                'message': f'Erro ao salvar nota: {str(e)}',
                'error_detail': error_detail,
                'debug_info': {
                    'aluno_id': data.get('aluno_id'),
                    'avaliacao_id': data.get('avaliacao_id'),
                    'nota_valor': data.get('nota'),
                    'turma_id': turma.id,
                    'disciplina_id': disciplina.id
                }
            })
    
    # Adicionar contagem real de notas para cada avaliação
    for avaliacao in avaliacoes:
        avaliacao.notas_existentes_count = NotaAvaliacao.objects.filter(
            avaliacao=avaliacao,
            nota__isnull=False
        ).count()
    
    # Buscar tipos de avaliação para o formulário
    tipos_avaliacao = TipoAvaliacao.objects.all().order_by('nome')
    
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisao': divisao,
        'alunos': alunos_list,
        'avaliacoes': avaliacoes,
        'notas_dict': notas_dict,
        'tipos_avaliacao': tipos_avaliacao,
        'page_title': f'Lançar Notas - {turma.nome}'
    }
    
    return render(request, 'diario/lancar_notas_diario.html', context)


@login_required
def gerenciar_avaliacoes_diario(request, turma_id):
    """Gerencia avaliações no contexto do diário"""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Obter disciplina da URL
    disciplina_id = request.GET.get('disciplina')
    if not disciplina_id:
        messages.error(request, 'Selecione uma disciplina para gerenciar avaliações.')
        return redirect('diario:turma', turma_id=turma_id)
    
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)

    # Obter divisão (opcional) da URL
    divisao_id = request.GET.get('divisao')
    if not divisao_id:
        messages.info(request, 'Selecione o período (bimestre/trimestre) para continuar.')
        return redirect('diario:disciplina', turma_id=turma.pk, disciplina_id=disciplina.pk)
    divisao = get_object_or_404(DivisaoPeriodoLetivo, pk=divisao_id)

    # Processar formulário de criação
    if request.method == 'POST':
        nome = request.POST.get('nome')
        tipo_avaliacao_id = request.POST.get('tipo_avaliacao')
        peso = request.POST.get('peso')
        data_aplicacao = request.POST.get('data_aplicacao')
        descricao = request.POST.get('descricao', '')
        
        if nome and tipo_avaliacao_id and peso and data_aplicacao:
            try:
                tipo_avaliacao = get_object_or_404(TipoAvaliacao, pk=tipo_avaliacao_id)
                
                avaliacao = Avaliacao.objects.create(
                    nome=nome,
                    descricao=descricao,
                    tipo_avaliacao=tipo_avaliacao,
                    turma=turma,
                    disciplina=disciplina,
                    divisao_periodo=divisao,
                    peso=float(peso),
                    data_aplicacao=data_aplicacao,
                    professor=request.user
                )
                
                messages.success(request, f'Avaliação "{nome}" criada com sucesso!')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': f'Avaliação "{nome}" criada com sucesso!'})

                return redirect(
                    f"{reverse('turma:gerenciar_avaliacoes_diario', args=[turma_id])}"
                    f"?disciplina={disciplina.pk}&divisao={divisao.pk}"
                )
                
            except Exception as e:
                error_msg = f'Erro ao criar avaliação: {str(e)}'
                messages.error(request, error_msg)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error_msg})
        else:
            error_msg = 'Preencha todos os campos obrigatórios.'
            messages.error(request, error_msg)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg})
    
    # Buscar avaliações da turma e disciplina
    avaliacoes = Avaliacao.objects.filter(
        turma=turma,
        disciplina=disciplina
    ).order_by('nome')
    
    # Adicionar contagem de notas para cada avaliação
    for avaliacao in avaliacoes:
        avaliacao.total_notas_lancadas = NotaAvaliacao.objects.filter(avaliacao=avaliacao).count()
    
    # Buscar tipos de avaliação
    tipos_avaliacao = TipoAvaliacao.objects.all().order_by('nome')
    
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisao': divisao,
        'avaliacoes': avaliacoes,
        'tipos_avaliacao': tipos_avaliacao,
        'page_title': f'Avaliações - {disciplina.nome} - {turma.nome}'
    }
    
    return render(request, 'diario/gerenciar_avaliacoes_diario.html', context)


@login_required
def visualizar_avaliacoes_diario(request, turma_id):
    """Visualiza avaliações no contexto do diário (Espelho do Diário)"""
    turma = get_object_or_404(Turma, pk=turma_id)

    # Obter disciplina da URL
    disciplina_id = request.GET.get('disciplina')
    if not disciplina_id:
        messages.error(request, 'Selecione uma disciplina para visualizar avaliações.')
        return redirect('diario:turma', turma_id=turma_id)

    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)

    # Obter divisão da URL
    divisao_id = request.GET.get('divisao')
    if not divisao_id:
        messages.info(request, 'Selecione o período (bimestre/trimestre) para continuar.')
        return redirect('diario:disciplina', turma_id=turma.pk, disciplina_id=disciplina.pk)
    divisao = get_object_or_404(DivisaoPeriodoLetivo, pk=divisao_id)

    # Buscar avaliações da turma e disciplina
    avaliacoes = Avaliacao.objects.filter(
        turma=turma,
        disciplina=disciplina
    ).order_by('nome')

    # Adicionar contagem de notas para cada avaliação
    for avaliacao in avaliacoes:
        avaliacao.total_notas_lancadas = NotaAvaliacao.objects.filter(avaliacao=avaliacao).count()

    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisao': divisao,
        'avaliacoes': avaliacoes,
        'page_title': f'Espelho do Diário - {disciplina.nome} - {turma.nome}'
    }

    return render(request, 'diario/visualizar_avaliacoes_diario.html', context)


@login_required
def editar_avaliacao_diario(request, avaliacao_id):
    """Edita avaliação no contexto do diário"""
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    
    # Dados para preservar valores em caso de erro
    form_data = {
        'nome': avaliacao.nome,
        'descricao': avaliacao.descricao,
        'tipo_avaliacao_id': avaliacao.tipo_avaliacao.pk if avaliacao.tipo_avaliacao else None,
        'peso': avaliacao.peso,
        'data_aplicacao': avaliacao.data_aplicacao
    }
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        tipo_avaliacao_id = request.POST.get('tipo_avaliacao')
        peso = request.POST.get('peso')
        data_aplicacao = request.POST.get('data_aplicacao')
        descricao = request.POST.get('descricao', '')
        
        # Atualizar form_data com os valores POST para preservar em caso de erro
        form_data.update({
            'nome': nome,
            'descricao': descricao,
            'tipo_avaliacao_id': tipo_avaliacao_id,
            'peso': peso if peso else avaliacao.peso,  # Preserva peso original se vazio
            'data_aplicacao': data_aplicacao
        })
        
        # Validação mais robusta para o campo peso
        if nome and tipo_avaliacao_id and peso is not None and peso != '' and data_aplicacao:
            try:
                # Validar se o peso é um número válido
                peso_float = float(peso)
                if peso_float <= 0:
                    raise ValueError("Peso deve ser maior que zero")
                    
                tipo_avaliacao = get_object_or_404(TipoAvaliacao, pk=tipo_avaliacao_id)
                
                avaliacao.nome = nome
                avaliacao.descricao = descricao
                avaliacao.tipo_avaliacao = tipo_avaliacao
                avaliacao.peso = peso_float
                avaliacao.data_aplicacao = data_aplicacao
                avaliacao.save()
                
                messages.success(request, f'Avaliação "{nome}" atualizada com sucesso!')
                return redirect(
                    f"{reverse('turma:gerenciar_avaliacoes_diario', args=[avaliacao.turma.pk])}"
                    f"?disciplina={avaliacao.disciplina.pk}&divisao={avaliacao.divisao_periodo.pk}"
                )
                
            except Exception as e:
                messages.error(request, f'Erro ao atualizar avaliação: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    # Buscar tipos de avaliação
    tipos_avaliacao = TipoAvaliacao.objects.all().order_by('nome')
    
    context = {
        'avaliacao': avaliacao,
        'form_data': form_data,  # Dados para preservar valores no formulário
        'turma': avaliacao.turma,
        'disciplina': avaliacao.disciplina,
        'tipos_avaliacao': tipos_avaliacao,
        'page_title': f'Editar Avaliação - {avaliacao.nome}'
    }
    
    return render(request, 'diario/editar_avaliacao_diario.html', context)


@login_required
@require_POST
def excluir_avaliacao_diario(request, avaliacao_id):
    """Exclui avaliação no contexto do diário (somente via POST)"""
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    turma_id = avaliacao.turma.pk
    destino = (
        f"{reverse('turma:gerenciar_avaliacoes_diario', args=[turma_id])}"
        f"?disciplina={avaliacao.disciplina.pk}&divisao={avaliacao.divisao_periodo.pk}"
    )
    nome_avaliacao = avaliacao.nome
    avaliacao.delete()

    success_msg = f'Avaliação "{nome_avaliacao}" excluída com sucesso!'
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': success_msg})
    messages.success(request, success_msg)
    return redirect(destino)
