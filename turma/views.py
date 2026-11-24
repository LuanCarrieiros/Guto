from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Avg, Q
from django.db import models
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import date
from .models import (
    Conceito, Turma, Disciplina, Enturmacao, TipoAvaliacao,
    Avaliacao, DivisaoPeriodoLetivo, NotaAvaliacao
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
    total_lancamentos = NotaAvaliacao.objects.count()
    # Avaliações já aplicadas que ainda não têm todas as notas lançadas
    pendencias = Avaliacao.objects.filter(ativo=True, notas_lancadas=False, data_aplicacao__lte=date.today()).count()
    
    # Turmas recentes
    turmas_recentes = Turma.objects.order_by('-id')[:5]
    
    # Lançamentos recentes
    lancamentos_recentes = NotaAvaliacao.objects.select_related(
        'aluno', 'avaliacao__disciplina'
    ).order_by('-data_atualizacao')[:5]
    
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
    """Lista as notas lançadas no diário"""
    lancamentos = NotaAvaliacao.objects.select_related(
        'aluno', 'conceito', 'usuario_lancamento', 'avaliacao__turma', 'avaliacao__disciplina'
    ).order_by('-data_atualizacao')

    # Filtros
    turma_id = request.GET.get('turma')
    disciplina_id = request.GET.get('disciplina')

    if turma_id:
        lancamentos = lancamentos.filter(avaliacao__turma_id=turma_id)
    if disciplina_id:
        lancamentos = lancamentos.filter(avaliacao__disciplina_id=disciplina_id)
    
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
    return redirect('diario:editar_avaliacao', avaliacao_id=pk)


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
