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
    Enturmacao, AulaRegistrada, RegistroFrequencia, TipoAvaliacao,
    Avaliacao, NotaAvaliacao, RelatorioFrequencia, DivisaoPeriodoLetivo
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


# ==================== DIÁRIO ELETRÔNICO ====================

@login_required
def diario_dashboard(request):
    """
    Dashboard principal do diário eletrônico - estilo Canvas
    """
    # Turmas do professor (se for professor) ou todas (se for admin/coordenador)
    if request.user.groups.filter(name='Professor').exists():
        # Buscar turmas onde o usuário é professor em alguma aula
        turmas_ids = AulaRegistrada.objects.filter(
            professor=request.user
        ).values_list('turma', flat=True).distinct()
        turmas = Turma.objects.filter(id__in=turmas_ids)
    else:
        turmas = Turma.objects.all()[:12]  # Limite para performance
    
    # Estatísticas rápidas
    total_turmas = turmas.count()
    aulas_hoje = AulaRegistrada.objects.filter(
        data_aula=date.today(),
        professor=request.user if request.user.groups.filter(name='Professor').exists() else None
    ).count()
    
    avaliacoes_pendentes = Avaliacao.objects.filter(
        notas_lancadas=False,
        data_aplicacao__lte=date.today()
    )
    if request.user.groups.filter(name='Professor').exists():
        avaliacoes_pendentes = avaliacoes_pendentes.filter(professor=request.user)
    
    # Atividades recentes
    aulas_recentes = AulaRegistrada.objects.filter(
        professor=request.user if request.user.groups.filter(name='Professor').exists() else None
    ).order_by('-data_aula', '-horario_inicio')[:8]
    
    context = {
        'turmas': turmas,
        'total_turmas': total_turmas,
        'aulas_hoje': aulas_hoje,
        'avaliacoes_pendentes': avaliacoes_pendentes.count(),
        'avaliacoes_pendentes_list': avaliacoes_pendentes[:5],
        'aulas_recentes': aulas_recentes,
    }
    
    return render(request, 'avaliacao/diario_dashboard.html', context)


@login_required
def turma_diario(request, turma_id):
    """
    Diário específico de uma turma - visão completa
    """
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Verificar permissões (simplificado)
    if request.user.groups.filter(name='Professor').exists():
        if not AulaRegistrada.objects.filter(turma=turma, professor=request.user).exists():
            messages.error(request, 'Você não tem permissão para acessar esta turma.')
            return redirect('avaliacao:diario_dashboard')
    
    # Alunos da turma
    alunos = turma.get_alunos_enturmados().order_by('nome')
    
    # Disciplinas da turma (baseado nas aulas registradas)
    disciplinas = Disciplina.objects.filter(
        aularegistrada__turma=turma
    ).distinct().order_by('nome')
    
    # Aulas recentes
    aulas_recentes = AulaRegistrada.objects.filter(
        turma=turma
    ).order_by('-data_aula', '-horario_inicio')[:10]
    
    # Avaliações da turma
    avaliacoes_recentes = Avaliacao.objects.filter(
        turma=turma
    ).order_by('-data_aplicacao')[:5]
    
    # Estatísticas
    total_aulas = AulaRegistrada.objects.filter(turma=turma).count()
    total_avaliacoes = Avaliacao.objects.filter(turma=turma).count()
    
    context = {
        'turma': turma,
        'alunos': alunos,
        'disciplinas': disciplinas,
        'aulas_recentes': aulas_recentes,
        'avaliacoes_recentes': avaliacoes_recentes,
        'total_aulas': total_aulas,
        'total_avaliacoes': total_avaliacoes,
        'total_alunos': alunos.count(),
    }
    
    return render(request, 'avaliacao/turma_diario.html', context)


@login_required
def registrar_aula(request, turma_id=None):
    """
    Registrar nova aula
    """
    turma = None
    if turma_id:
        turma = get_object_or_404(Turma, pk=turma_id)
    
    if request.method == 'POST':
        turma_id = request.POST.get('turma')
        disciplina_id = request.POST.get('disciplina')
        data_aula = request.POST.get('data_aula')
        horario_inicio = request.POST.get('horario_inicio')
        horario_fim = request.POST.get('horario_fim')
        conteudo = request.POST.get('conteudo_programatico')
        observacoes = request.POST.get('observacoes', '')
        
        if turma_id and disciplina_id and data_aula and horario_inicio and horario_fim and conteudo:
            turma_obj = get_object_or_404(Turma, pk=turma_id)
            disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
            
            # Criar a aula
            aula = AulaRegistrada.objects.create(
                turma=turma_obj,
                disciplina=disciplina,
                professor=request.user,
                data_aula=data_aula,
                horario_inicio=horario_inicio,
                horario_fim=horario_fim,
                conteudo_programatico=conteudo,
                observacoes=observacoes
            )
            
            # Registrar atividade
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='REGISTRAR_AULA',
                modulo='AVALIACAO',
                objeto_nome=f'{disciplina.nome} - {turma_obj.nome}',
                objeto_id=aula.id,
                descricao=f'Aula registrada: {disciplina.nome} em {data_aula}'
            )
            
            messages.success(request, 'Aula registrada com sucesso!')
            
            # Perguntar se quer fazer a chamada agora
            if 'fazer_chamada' in request.POST:
                return redirect('avaliacao:fazer_chamada', aula_id=aula.id)
            
            return redirect('avaliacao:turma_diario', turma_id=turma_obj.id)
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    # Buscar turmas e disciplinas para o formulário
    if request.user.groups.filter(name='Professor').exists():
        turmas = Turma.objects.filter(
            aulas__professor=request.user
        ).distinct() if not turma else [turma]
    else:
        turmas = Turma.objects.all()
    
    disciplinas = Disciplina.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'turma': turma,
        'turmas': turmas,
        'disciplinas': disciplinas,
    }
    
    return render(request, 'avaliacao/registrar_aula.html', context)


@login_required
def fazer_chamada(request, aula_id):
    """
    Interface para fazer chamada de uma aula
    """
    aula = get_object_or_404(AulaRegistrada, pk=aula_id)
    
    # Verificar permissões
    if request.user.groups.filter(name='Professor').exists() and aula.professor != request.user:
        messages.error(request, 'Você não tem permissão para fazer chamada desta aula.')
        return redirect('avaliacao:diario_dashboard')
    
    # Alunos da turma
    alunos = aula.turma.get_alunos_enturmados().order_by('nome')
    
    # Registros de frequência existentes
    frequencias_existentes = RegistroFrequencia.objects.filter(
        aula=aula
    ).values_list('aluno_id', 'situacao')
    frequencias_dict = dict(frequencias_existentes)
    
    if request.method == 'POST':
        # Processar a chamada
        for aluno in alunos:
            situacao = request.POST.get(f'situacao_{aluno.id}', 'PRESENTE')
            observacoes = request.POST.get(f'observacoes_{aluno.id}', '')
            
            # Criar ou atualizar registro de frequência
            registro, created = RegistroFrequencia.objects.get_or_create(
                aula=aula,
                aluno=aluno,
                defaults={
                    'situacao': situacao,
                    'observacoes': observacoes,
                    'usuario_registro': request.user
                }
            )
            
            if not created:
                registro.situacao = situacao
                registro.observacoes = observacoes
                registro.save()
        
        # Marcar chamada como realizada
        aula.chamada_realizada = True
        aula.save()
        
        # Registrar atividade
        AtividadeRecente.registrar_atividade(
            usuario=request.user,
            acao='FAZER_CHAMADA',
            modulo='AVALIACAO',
            objeto_nome=f'{aula.disciplina.nome} - {aula.turma.nome}',
            objeto_id=aula.id,
            descricao=f'Chamada realizada para {aula.data_aula.strftime("%d/%m/%Y")}'
        )
        
        messages.success(request, 'Chamada realizada com sucesso!')
        return redirect('avaliacao:turma_diario', turma_id=aula.turma.id)
    
    context = {
        'aula': aula,
        'alunos': alunos,
        'frequencias_dict': frequencias_dict,
        'situacao_choices': RegistroFrequencia.SITUACAO_CHOICES,
    }
    
    return render(request, 'avaliacao/fazer_chamada.html', context)


@login_required
def criar_avaliacao(request, turma_id=None):
    """
    Criar nova avaliação
    """
    turma = None
    if turma_id:
        turma = get_object_or_404(Turma, pk=turma_id)
    
    if request.method == 'POST':
        turma_id = request.POST.get('turma')
        disciplina_id = request.POST.get('disciplina')
        divisao_periodo_id = request.POST.get('divisao_periodo')
        tipo_avaliacao_id = request.POST.get('tipo_avaliacao')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        data_aplicacao = request.POST.get('data_aplicacao')
        valor_maximo = request.POST.get('valor_maximo', '10.00')
        peso = request.POST.get('peso', '1.0')
        
        if all([turma_id, disciplina_id, divisao_periodo_id, tipo_avaliacao_id, nome, data_aplicacao]):
            turma_obj = get_object_or_404(Turma, pk=turma_id)
            disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
            divisao_periodo = get_object_or_404(DivisaoPeriodoLetivo, pk=divisao_periodo_id)
            tipo_avaliacao = get_object_or_404(TipoAvaliacao, pk=tipo_avaliacao_id)
            
            avaliacao = Avaliacao.objects.create(
                turma=turma_obj,
                disciplina=disciplina,
                divisao_periodo=divisao_periodo,
                tipo_avaliacao=tipo_avaliacao,
                professor=request.user,
                nome=nome,
                descricao=descricao,
                data_aplicacao=data_aplicacao,
                valor_maximo=valor_maximo,
                peso=peso
            )
            
            # Criar registros de notas para todos os alunos da turma
            alunos = turma_obj.get_alunos_enturmados()
            for aluno in alunos:
                NotaAvaliacao.objects.create(
                    avaliacao=avaliacao,
                    aluno=aluno,
                    usuario_lancamento=request.user
                )
            
            # Registrar atividade
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='CRIAR_AVALIACAO',
                modulo='AVALIACAO',
                objeto_nome=nome,
                objeto_id=avaliacao.id,
                descricao=f'Avaliação criada: {nome} - {turma_obj.nome}'
            )
            
            messages.success(request, 'Avaliação criada com sucesso!')
            return redirect('avaliacao:lancar_notas_avaliacao', avaliacao_id=avaliacao.id)
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    # Dados para o formulário
    if request.user.groups.filter(name='Professor').exists():
        turmas = Turma.objects.filter(
            aulas__professor=request.user
        ).distinct() if not turma else [turma]
    else:
        turmas = Turma.objects.all()
    
    disciplinas = Disciplina.objects.filter(ativo=True).order_by('nome')
    divisoes_periodo = DivisaoPeriodoLetivo.objects.filter(ativo=True).order_by('periodo_letivo', 'ordem')
    tipos_avaliacao = TipoAvaliacao.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'turma': turma,
        'turmas': turmas,
        'disciplinas': disciplinas,
        'divisoes_periodo': divisoes_periodo,
        'tipos_avaliacao': tipos_avaliacao,
    }
    
    return render(request, 'avaliacao/criar_avaliacao.html', context)


@login_required
def lancar_notas_avaliacao(request, avaliacao_id):
    """
    Lançar notas de uma avaliação específica
    """
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    
    # Verificar permissões
    if request.user.groups.filter(name='Professor').exists() and avaliacao.professor != request.user:
        messages.error(request, 'Você não tem permissão para lançar notas desta avaliação.')
        return redirect('avaliacao:diario_dashboard')
    
    # Notas da avaliação
    notas = NotaAvaliacao.objects.filter(avaliacao=avaliacao).order_by('aluno__nome')
    
    if request.method == 'POST':
        alguma_alteracao = False
        
        for nota in notas:
            # Dados do POST
            nota_valor = request.POST.get(f'nota_{nota.id}')
            conceito_id = request.POST.get(f'conceito_{nota.id}')
            ausente = 'ausente' in request.POST.getlist(f'ausente_{nota.id}')
            dispensado = 'dispensado' in request.POST.getlist(f'dispensado_{nota.id}')
            observacoes = request.POST.get(f'observacoes_{nota.id}', '')
            
            # Atualizar nota
            if nota_valor and not ausente and not dispensado:
                nota.nota = float(nota_valor)
                nota.conceito = None
            elif conceito_id and not ausente and not dispensado:
                nota.conceito_id = int(conceito_id)
                nota.nota = None
            else:
                nota.nota = None
                nota.conceito = None
            
            nota.ausente = ausente
            nota.dispensado = dispensado
            nota.observacoes = observacoes
            nota.save()
            alguma_alteracao = True
        
        if alguma_alteracao:
            # Marcar avaliação como tendo notas lançadas
            avaliacao.notas_lancadas = True
            avaliacao.save()
            
            # Registrar atividade
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='LANCAR_NOTAS',
                modulo='AVALIACAO',
                objeto_nome=avaliacao.nome,
                objeto_id=avaliacao.id,
                descricao=f'Notas lançadas: {avaliacao.nome}'
            )
            
            messages.success(request, 'Notas lançadas com sucesso!')
            return redirect('avaliacao:turma_diario', turma_id=avaliacao.turma.id)
    
    # Conceitos disponíveis
    conceitos = Conceito.objects.filter(ativo=True).order_by('valor_numerico')
    
    context = {
        'avaliacao': avaliacao,
        'notas': notas,
        'conceitos': conceitos,
        'usa_conceitos': avaliacao.disciplina.avalia_por_conceito,
    }
    
    return render(request, 'avaliacao/lancar_notas_avaliacao.html', context)


@login_required
def relatorio_frequencia(request, turma_id=None, aluno_id=None):
    """
    Relatório de frequência
    """
    turma = None
    aluno = None
    
    if turma_id:
        turma = get_object_or_404(Turma, pk=turma_id)
    if aluno_id:
        aluno = get_object_or_404(Aluno, pk=aluno_id)
    
    # Filtros
    disciplina_id = request.GET.get('disciplina')
    periodo_id = request.GET.get('periodo')
    
    # Query base
    frequencias = RegistroFrequencia.objects.select_related(
        'aula__turma', 'aula__disciplina', 'aluno'
    )
    
    if turma:
        frequencias = frequencias.filter(aula__turma=turma)
    if aluno:
        frequencias = frequencias.filter(aluno=aluno)
    if disciplina_id:
        frequencias = frequencias.filter(aula__disciplina_id=disciplina_id)
    
    # Estatísticas
    total_registros = frequencias.count()
    presencas = frequencias.filter(situacao='PRESENTE').count()
    faltas = frequencias.filter(situacao='AUSENTE').count()
    justificadas = frequencias.filter(situacao='JUSTIFICADO').count()
    
    percentual_frequencia = round((presencas / total_registros) * 100, 2) if total_registros > 0 else 0
    
    # Dados para filtros
    disciplinas = Disciplina.objects.all().order_by('nome')
    periodos = DivisaoPeriodoLetivo.objects.filter(ativo=True).order_by('periodo_letivo', 'ordem')
    
    context = {
        'turma': turma,
        'aluno': aluno,
        'frequencias': frequencias.order_by('-aula__data_aula')[:100],  # Limitar para performance
        'total_registros': total_registros,
        'presencas': presencas,
        'faltas': faltas,
        'justificadas': justificadas,
        'percentual_frequencia': percentual_frequencia,
        'disciplinas': disciplinas,
        'periodos': periodos,
        'disciplina_selecionada': disciplina_id,
        'periodo_selecionado': periodo_id,
    }
    
    return render(request, 'avaliacao/relatorio_frequencia.html', context)