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
def disciplina_create(request):
    """
    Criar nova disciplina
    """
    if request.method == 'POST':
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            disciplina = form.save(commit=False)
            disciplina.usuario_criacao = request.user
            disciplina.save()
            
            # Registrar atividade recente
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='CRIAR',
                modulo='AVALIACAO',
                objeto_nome=disciplina.nome,
                objeto_id=disciplina.id,
                descricao=f'Nova disciplina criada: {disciplina.nome}'
            )
            
            messages.success(request, 'Disciplina criada com sucesso!')
            return redirect('avaliacao:disciplinas_list')
    else:
        form = DisciplinaForm()
    
    return render(request, 'avaliacao/disciplina_form.html', {
        'form': form,
        'title': 'Criar Nova Disciplina',
        'is_create': True
    })


@login_required
def disciplina_edit(request, pk):
    """
    Editar disciplina
    """
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    if request.method == 'POST':
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            form.save()
            
            # Registrar atividade recente
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='EDITAR',
                modulo='AVALIACAO',
                objeto_nome=disciplina.nome,
                objeto_id=disciplina.id,
                descricao=f'Disciplina editada: {disciplina.nome}'
            )
            
            messages.success(request, 'Disciplina editada com sucesso!')
            return redirect('avaliacao:disciplinas_list')
    else:
        form = DisciplinaForm(instance=disciplina)
    
    return render(request, 'avaliacao/disciplina_form.html', {
        'form': form,
        'disciplina': disciplina,
        'title': f'Editar Disciplina - {disciplina.nome}',
        'is_create': False
    })


@login_required
def disciplina_delete(request, pk):
    """
    Excluir disciplina
    """
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    if request.method == 'POST':
        nome_disciplina = disciplina.nome
        disciplina.delete()
        
        # Registrar atividade recente
        AtividadeRecente.registrar_atividade(
            usuario=request.user,
            acao='DELETAR',
            modulo='AVALIACAO',
            objeto_nome=nome_disciplina,
            objeto_id=pk,
            descricao=f'Disciplina excluída: {nome_disciplina}'
        )
        
        messages.success(request, f'Disciplina {nome_disciplina} excluída com sucesso!')
        return redirect('avaliacao:disciplinas_list')
    
    return render(request, 'avaliacao/disciplina_confirm_delete.html', {'disciplina': disciplina})


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
    Lista de avaliações para lançamento de notas
    """
    # Buscar avaliações criadas
    avaliacoes = Avaliacao.objects.select_related('turma', 'disciplina', 'tipo_avaliacao').order_by('-data_aplicacao')
    
    # Filtros
    turma_id = request.GET.get('turma', '')
    disciplina_id = request.GET.get('disciplina', '')
    
    if turma_id:
        avaliacoes = avaliacoes.filter(turma_id=turma_id)
    if disciplina_id:
        avaliacoes = avaliacoes.filter(disciplina_id=disciplina_id)
    
    # Dados para filtros
    turmas = Turma.objects.all()
    disciplinas = Disciplina.objects.filter(ativo=True)
    
    context = {
        'avaliacoes': avaliacoes,
        'turmas': turmas,
        'disciplinas': disciplinas,
        'turma_selecionada': turma_id,
        'disciplina_selecionada': disciplina_id,
    }
    
    return render(request, 'avaliacao/lancar_notas.html', context)


@login_required
def avaliacao_create(request):
    """
    Criar nova avaliação/atividade
    """
    if request.method == 'POST':
        turma_id = request.POST.get('turma')
        disciplina_id = request.POST.get('disciplina')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        data_aplicacao = request.POST.get('data_aplicacao')
        valor_maximo = request.POST.get('valor_maximo', '10.00')
        tipo_avaliacao_id = request.POST.get('tipo_avaliacao', 1)  # Default para primeiro tipo
        
        if turma_id and disciplina_id and nome and data_aplicacao:
            try:
                turma = get_object_or_404(Turma, id=turma_id)
                disciplina = get_object_or_404(Disciplina, id=disciplina_id)
                tipo_avaliacao = get_object_or_404(TipoAvaliacao, id=tipo_avaliacao_id)
                
                avaliacao = Avaliacao.objects.create(
                    turma=turma,
                    disciplina=disciplina,
                    tipo_avaliacao=tipo_avaliacao,
                    professor=request.user,
                    nome=nome,
                    descricao=descricao,
                    data_aplicacao=data_aplicacao,
                    valor_maximo=valor_maximo,
                    peso=1.0
                )
                
                # Criar registros de notas para todos os alunos da turma
                alunos = turma.get_alunos_enturmados()
                for aluno in alunos:
                    NotaAvaliacao.objects.create(
                        avaliacao=avaliacao,
                        aluno=aluno,
                        usuario_lancamento=request.user
                    )
                
                # Registrar atividade recente
                AtividadeRecente.registrar_atividade(
                    usuario=request.user,
                    acao='CRIAR',
                    modulo='AVALIACAO',
                    objeto_nome=nome,
                    objeto_id=avaliacao.id,
                    descricao=f'Avaliação criada: {nome} - {turma.nome}'
                )
                
                messages.success(request, 'Avaliação criada com sucesso! Agora você pode lançar as notas.')
                return redirect('avaliacao:lancar_notas_avaliacao', avaliacao_id=avaliacao.id)
            except Exception as e:
                messages.error(request, f'Erro ao criar avaliação: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    # Dados para o formulário
    turmas = Turma.objects.all()
    disciplinas = Disciplina.objects.filter(ativo=True)
    tipos_avaliacao = TipoAvaliacao.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'turmas': turmas,
        'disciplinas': disciplinas,
        'tipos_avaliacao': tipos_avaliacao,
    }
    
    return render(request, 'avaliacao/avaliacao_create.html', context)


@login_required
def conceitos_list(request):
    """
    Lista todos os conceitos
    """
    conceitos = Conceito.objects.all().order_by('valor_numerico')
    
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
            avg_valor=Avg('conceito__valor_numerico')
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
    disciplinas = Disciplina.objects.filter(ativo=True).order_by('nome')
    
    # Conteúdos recentes
    conteudos_recentes = ConteudoAula.objects.order_by('-data_aula')[:10]
    
    if request.method == 'POST':
        turma_id = request.POST.get('turma')
        disciplina_id = request.POST.get('disciplina')
        data_aula = request.POST.get('data_aula')
        conteudo = request.POST.get('conteudo')
        
        if turma_id and disciplina_id and data_aula and conteudo:
            try:
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
            except Exception as e:
                messages.error(request, 'Erro ao registrar conteúdo. Verifique se a turma e disciplina existem.')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    context = {
        'turmas': turmas,
        'disciplinas': disciplinas,
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
            try:
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
            except Exception as e:
                messages.error(request, f'Erro ao registrar aula: {str(e)}')
        else:
            campos_faltantes = []
            if not turma_id: campos_faltantes.append('Turma')
            if not disciplina_id: campos_faltantes.append('Disciplina') 
            if not data_aula: campos_faltantes.append('Data da aula')
            if not horario_inicio: campos_faltantes.append('Horário de início')
            if not horario_fim: campos_faltantes.append('Horário de fim')
            if not conteudo: campos_faltantes.append('Conteúdo programático')
            
            messages.error(request, f'Campos obrigatórios não preenchidos: {", ".join(campos_faltantes)}')
    
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


@login_required
def gerenciar_disciplinas_turma(request, turma_id):
    """
    Gerenciar disciplinas específicas de uma turma
    """
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Disciplinas disponíveis para esta turma
    disciplinas = Disciplina.objects.filter(ativo=True).order_by('nome')
    
    # Disciplinas já associadas a esta turma (através de aulas ou avaliações)
    disciplinas_associadas = Disciplina.objects.filter(
        models.Q(aularegistrada__turma=turma) | 
        models.Q(avaliacao__turma=turma)
    ).distinct().order_by('nome')
    
    # Estatísticas
    total_disciplinas = disciplinas.count()
    disciplinas_em_uso = disciplinas_associadas.count()
    disciplinas_disponiveis = total_disciplinas - disciplinas_em_uso
    
    context = {
        'turma': turma,
        'disciplinas': disciplinas,
        'disciplinas_associadas': disciplinas_associadas,
        'total_disciplinas': total_disciplinas,
        'disciplinas_em_uso': disciplinas_em_uso,
        'disciplinas_disponiveis': disciplinas_disponiveis,
    }
    
    return render(request, 'avaliacao/gerenciar_disciplinas_turma.html', context)


@login_required
def diario_online_turma(request, turma_id):
    """
    Diário online específico para uma turma
    """
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Verificar permissões básicas
    if request.user.groups.filter(name='Professor').exists():
        # Professor só pode ver turmas onde tem aulas
        if not AulaRegistrada.objects.filter(turma=turma, professor=request.user).exists():
            messages.warning(request, 'Você não tem permissão para acessar o diário desta turma.')
            return redirect('avaliacao:turma_detail', pk=turma_id)
    
    # Disciplinas desta turma (baseado em aulas registradas)
    disciplinas = Disciplina.objects.filter(
        aularegistrada__turma=turma
    ).distinct().order_by('nome')
    
    # Se não há disciplinas, mostrar todas disponíveis para começar
    if not disciplinas.exists():
        disciplinas = Disciplina.objects.filter(ativo=True).order_by('nome')
    
    # Aulas recentes desta turma
    aulas_recentes = AulaRegistrada.objects.filter(
        turma=turma
    ).select_related('disciplina', 'professor').order_by('-data_aula', '-horario_inicio')[:10]
    
    # Avaliações recentes desta turma
    avaliacoes_recentes = Avaliacao.objects.filter(
        turma=turma
    ).select_related('disciplina', 'professor').order_by('-data_aplicacao')[:5]
    
    # Estatísticas
    total_aulas = AulaRegistrada.objects.filter(turma=turma).count()
    total_avaliacoes = Avaliacao.objects.filter(turma=turma).count()
    alunos_enturmados = turma.get_alunos_enturmados().count()
    
    # Formulário de registro de conteúdo
    if request.method == 'POST':
        disciplina_id = request.POST.get('disciplina')
        data_aula = request.POST.get('data_aula')
        conteudo = request.POST.get('conteudo')
        
        if disciplina_id and data_aula and conteudo:
            try:
                disciplina = get_object_or_404(Disciplina, id=disciplina_id)
                
                ConteudoAula.objects.create(
                    turma=turma,
                    disciplina=disciplina,
                    data_aula=data_aula,
                    conteudo=conteudo,
                    usuario_registro=request.user
                )
                
                # Registrar atividade
                AtividadeRecente.registrar_atividade(
                    usuario=request.user,
                    acao='REGISTRO_CONTEUDO',
                    modulo='AVALIACAO',
                    objeto_nome=f'{disciplina.nome} - {turma.nome}',
                    objeto_id=turma.id,
                    descricao=f'Conteúdo registrado para {data_aula}'
                )
                
                messages.success(request, 'Conteúdo registrado com sucesso!')
                return redirect('avaliacao:diario_online_turma', turma_id=turma.id)
            except Exception as e:
                messages.error(request, 'Erro ao registrar conteúdo.')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    context = {
        'turma': turma,
        'disciplinas': disciplinas,
        'aulas_recentes': aulas_recentes,
        'avaliacoes_recentes': avaliacoes_recentes,
        'total_aulas': total_aulas,
        'total_avaliacoes': total_avaliacoes,
        'alunos_enturmados': alunos_enturmados,
    }
    
    return render(request, 'avaliacao/diario_online_turma.html', context)


# ==================== AVALIAÇÕES CRUD ====================

@login_required
def avaliacoes_list(request):
    """
    Lista todas as avaliações do sistema
    """
    avaliacoes = Avaliacao.objects.select_related(
        'turma', 'disciplina', 'professor', 'tipo_avaliacao'
    ).order_by('-data_aplicacao')
    
    # Filtros
    turma_id = request.GET.get('turma', '')
    disciplina_id = request.GET.get('disciplina', '')
    status = request.GET.get('status', '')
    
    if turma_id:
        avaliacoes = avaliacoes.filter(turma_id=turma_id)
    if disciplina_id:
        avaliacoes = avaliacoes.filter(disciplina_id=disciplina_id)
    if status == 'lancadas':
        avaliacoes = avaliacoes.filter(notas_lancadas=True)
    elif status == 'pendentes':
        avaliacoes = avaliacoes.filter(notas_lancadas=False)
    
    # Paginação
    paginator = Paginator(avaliacoes, 20)
    page_number = request.GET.get('page')
    avaliacoes_page = paginator.get_page(page_number)
    
    # Dados para filtros
    turmas = Turma.objects.all().order_by('nome')
    disciplinas = Disciplina.objects.filter(ativo=True).order_by('nome')
    
    # Estatísticas
    total_avaliacoes = Avaliacao.objects.count()
    avaliacoes_pendentes = Avaliacao.objects.filter(notas_lancadas=False).count()
    avaliacoes_concluidas = Avaliacao.objects.filter(notas_lancadas=True).count()
    
    context = {
        'avaliacoes': avaliacoes_page,
        'turmas': turmas,
        'disciplinas': disciplinas,
        'turma_selecionada': turma_id,
        'disciplina_selecionada': disciplina_id,
        'status_selecionado': status,
        'total_avaliacoes': total_avaliacoes,
        'avaliacoes_pendentes': avaliacoes_pendentes,
        'avaliacoes_concluidas': avaliacoes_concluidas,
    }
    
    return render(request, 'avaliacao/avaliacoes_list.html', context)


@login_required
def avaliacao_detail(request, pk):
    """
    Detalhes de uma avaliação específica
    """
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    
    # Notas da avaliação
    notas = NotaAvaliacao.objects.filter(avaliacao=avaliacao).select_related('aluno').order_by('aluno__nome')
    
    # Estatísticas
    total_notas = notas.count()
    notas_lancadas = notas.filter(models.Q(nota__isnull=False) | models.Q(conceito__isnull=False)).count()
    ausentes = notas.filter(ausente=True).count()
    dispensados = notas.filter(dispensado=True).count()
    
    # Média da turma
    notas_numericas = notas.filter(nota__isnull=False).values_list('nota', flat=True)
    media_turma = sum(notas_numericas) / len(notas_numericas) if notas_numericas else 0
    
    context = {
        'avaliacao': avaliacao,
        'notas': notas,
        'total_notas': total_notas,
        'notas_lancadas': notas_lancadas,
        'ausentes': ausentes,
        'dispensados': dispensados,
        'media_turma': round(media_turma, 2),
        'percentual_lancamento': round((notas_lancadas / total_notas) * 100, 1) if total_notas > 0 else 0,
    }
    
    return render(request, 'avaliacao/avaliacao_detail.html', context)


@login_required
def avaliacao_edit(request, pk):
    """
    Editar uma avaliação
    """
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    
    # Verificar permissões
    if request.user.groups.filter(name='Professor').exists() and avaliacao.professor != request.user:
        messages.error(request, 'Você não tem permissão para editar esta avaliação.')
        return redirect('avaliacao:avaliacao_detail', pk=pk)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        data_aplicacao = request.POST.get('data_aplicacao')
        valor_maximo = request.POST.get('valor_maximo')
        peso = request.POST.get('peso', '1.0')
        tipo_avaliacao_id = request.POST.get('tipo_avaliacao')
        
        if nome and data_aplicacao and valor_maximo:
            avaliacao.nome = nome
            avaliacao.descricao = descricao
            avaliacao.data_aplicacao = data_aplicacao
            avaliacao.valor_maximo = valor_maximo
            avaliacao.peso = peso
            
            if tipo_avaliacao_id:
                avaliacao.tipo_avaliacao_id = tipo_avaliacao_id
            
            avaliacao.save()
            
            # Registrar atividade
            AtividadeRecente.registrar_atividade(
                usuario=request.user,
                acao='EDITAR',
                modulo='AVALIACAO',
                objeto_nome=avaliacao.nome,
                objeto_id=avaliacao.id,
                descricao=f'Avaliação editada: {avaliacao.nome}'
            )
            
            messages.success(request, 'Avaliação editada com sucesso!')
            return redirect('avaliacao:avaliacao_detail', pk=pk)
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    # Dados para o formulário
    tipos_avaliacao = TipoAvaliacao.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'avaliacao': avaliacao,
        'tipos_avaliacao': tipos_avaliacao,
        'is_edit': True,
    }
    
    return render(request, 'avaliacao/avaliacao_form.html', context)


@login_required
def avaliacao_delete(request, pk):
    """
    Excluir uma avaliação
    """
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    
    # Verificar permissões
    if request.user.groups.filter(name='Professor').exists() and avaliacao.professor != request.user:
        messages.error(request, 'Você não tem permissão para excluir esta avaliação.')
        return redirect('avaliacao:avaliacao_detail', pk=pk)
    
    # Verificar se há notas lançadas
    if avaliacao.notas_lancadas:
        messages.error(request, 'Não é possível excluir uma avaliação que já possui notas lançadas.')
        return redirect('avaliacao:avaliacao_detail', pk=pk)
    
    if request.method == 'POST':
        nome_avaliacao = avaliacao.nome
        turma_id = avaliacao.turma.id
        
        # Excluir notas relacionadas primeiro
        NotaAvaliacao.objects.filter(avaliacao=avaliacao).delete()
        
        # Excluir a avaliação
        avaliacao.delete()
        
        # Registrar atividade
        AtividadeRecente.registrar_atividade(
            usuario=request.user,
            acao='DELETAR',
            modulo='AVALIACAO',
            objeto_nome=nome_avaliacao,
            objeto_id=pk,
            descricao=f'Avaliação excluída: {nome_avaliacao}'
        )
        
        messages.success(request, f'Avaliação "{nome_avaliacao}" excluída com sucesso!')
        return redirect('avaliacao:turma_detail', pk=turma_id)
    
    context = {
        'avaliacao': avaliacao,
    }
    
    return render(request, 'avaliacao/avaliacao_confirm_delete.html', context)


# ==================== RELATÓRIOS AVANÇADOS ====================

@login_required
def relatorio_desempenho(request):
    """
    Relatório de desempenho geral dos alunos
    """
    # Filtros
    turma_id = request.GET.get('turma', '')
    disciplina_id = request.GET.get('disciplina', '')
    periodo = request.GET.get('periodo', '')
    
    # Query base para notas
    notas = NotaAvaliacao.objects.select_related(
        'aluno', 'avaliacao__turma', 'avaliacao__disciplina'
    ).filter(models.Q(nota__isnull=False) | models.Q(conceito__isnull=False))
    
    if turma_id:
        notas = notas.filter(avaliacao__turma_id=turma_id)
    if disciplina_id:
        notas = notas.filter(avaliacao__disciplina_id=disciplina_id)
    
    # Estatísticas por aluno
    desempenho_alunos = []
    alunos_com_notas = notas.values_list('aluno', flat=True).distinct()
    
    for aluno_id in alunos_com_notas:
        aluno = Aluno.objects.get(id=aluno_id)
        notas_aluno = notas.filter(aluno_id=aluno_id, nota__isnull=False)
        
        if notas_aluno.exists():
            media = notas_aluno.aggregate(Avg('nota'))['nota__avg'] or 0
            total_avaliacoes = notas_aluno.count()
            
            desempenho_alunos.append({
                'aluno': aluno,
                'media': round(media, 2),
                'total_avaliacoes': total_avaliacoes,
                'status': 'Aprovado' if media >= 7.0 else 'Recuperação' if media >= 5.0 else 'Reprovado'
            })
    
    # Ordenar por média decrescente
    desempenho_alunos.sort(key=lambda x: x['media'], reverse=True)
    
    # Dados para filtros
    turmas = Turma.objects.all().order_by('nome')
    disciplinas = Disciplina.objects.filter(ativo=True).order_by('nome')
    
    # Estatísticas gerais
    total_alunos = len(desempenho_alunos)
    aprovados = len([d for d in desempenho_alunos if d['status'] == 'Aprovado'])
    reprovados = len([d for d in desempenho_alunos if d['status'] == 'Reprovado'])
    
    context = {
        'desempenho_alunos': desempenho_alunos,
        'turmas': turmas,
        'disciplinas': disciplinas,
        'turma_selecionada': turma_id,
        'disciplina_selecionada': disciplina_id,
        'total_alunos': total_alunos,
        'aprovados': aprovados,
        'reprovados': reprovados,
        'percentual_aprovacao': round((aprovados / total_alunos) * 100, 1) if total_alunos > 0 else 0,
    }
    
    return render(request, 'avaliacao/relatorio_desempenho.html', context)


@login_required
def gerar_boletim(request, aluno_id):
    """
    Gerar boletim individual do aluno
    """
    aluno = get_object_or_404(Aluno, id=aluno_id)
    
    # Buscar todas as notas do aluno
    notas = NotaAvaliacao.objects.filter(aluno=aluno).select_related(
        'avaliacao__disciplina', 'avaliacao__turma', 'avaliacao__tipo_avaliacao'
    ).order_by('avaliacao__disciplina__nome', 'avaliacao__data_aplicacao')
    
    # Organizar notas por disciplina
    notas_por_disciplina = {}
    for nota in notas:
        disciplina = nota.avaliacao.disciplina
        if disciplina not in notas_por_disciplina:
            notas_por_disciplina[disciplina] = []
        notas_por_disciplina[disciplina].append(nota)
    
    # Calcular médias por disciplina
    medias_disciplinas = {}
    for disciplina, notas_disc in notas_por_disciplina.items():
        notas_numericas = [n.nota for n in notas_disc if n.nota is not None]
        if notas_numericas:
            medias_disciplinas[disciplina] = {
                'media': round(sum(notas_numericas) / len(notas_numericas), 2),
                'total_avaliacoes': len(notas_numericas),
                'status': 'Aprovado' if sum(notas_numericas) / len(notas_numericas) >= 7.0 else 'Recuperação'
            }
    
    # Frequência do aluno
    registros_frequencia = RegistroFrequencia.objects.filter(aluno=aluno)
    total_aulas = registros_frequencia.count()
    presencas = registros_frequencia.filter(situacao='PRESENTE').count()
    frequencia_percentual = round((presencas / total_aulas) * 100, 1) if total_aulas > 0 else 0
    
    context = {
        'aluno': aluno,
        'notas_por_disciplina': notas_por_disciplina,
        'medias_disciplinas': medias_disciplinas,
        'total_aulas': total_aulas,
        'presencas': presencas,
        'frequencia_percentual': frequencia_percentual,
    }
    
    return render(request, 'avaliacao/boletim_aluno.html', context)


# ==================== OPERAÇÕES EM LOTE ====================

@login_required
def bulk_grade_entry(request, avaliacao_id):
    """
    Lançamento de notas em lote com upload de arquivo
    """
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    
    # Verificar permissões
    if request.user.groups.filter(name='Professor').exists() and avaliacao.professor != request.user:
        messages.error(request, 'Você não tem permissão para lançar notas desta avaliação.')
        return redirect('avaliacao:avaliacao_detail', pk=avaliacao_id)
    
    if request.method == 'POST':
        if 'bulk_action' in request.POST:
            action = request.POST.get('bulk_action')
            nota_valor = request.POST.get('bulk_nota', '')
            
            if action == 'set_all_present':
                # Marcar todos como presentes
                NotaAvaliacao.objects.filter(avaliacao=avaliacao).update(ausente=False)
                messages.success(request, 'Todos os alunos foram marcados como presentes.')
            
            elif action == 'set_grade_all' and nota_valor:
                # Aplicar nota para todos
                try:
                    nota = float(nota_valor)
                    if 0 <= nota <= avaliacao.valor_maximo:
                        NotaAvaliacao.objects.filter(avaliacao=avaliacao, ausente=False).update(
                            nota=nota, conceito=None
                        )
                        messages.success(request, f'Nota {nota} aplicada para todos os alunos presentes.')
                    else:
                        messages.error(request, f'Nota deve estar entre 0 e {avaliacao.valor_maximo}.')
                except ValueError:
                    messages.error(request, 'Valor de nota inválido.')
            
            return redirect('avaliacao:lancar_notas_avaliacao', avaliacao_id=avaliacao_id)
    
    # Notas da avaliação
    notas = NotaAvaliacao.objects.filter(avaliacao=avaliacao).select_related('aluno').order_by('aluno__nome')
    
    context = {
        'avaliacao': avaliacao,
        'notas': notas,
    }
    
    return render(request, 'avaliacao/bulk_grade_entry.html', context)


@login_required
def bulk_attendance(request, turma_id):
    """
    Lançamento de frequência em lote
    """
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Aulas recentes da turma sem chamada
    aulas_sem_chamada = AulaRegistrada.objects.filter(
        turma=turma, chamada_realizada=False
    ).order_by('-data_aula')[:10]
    
    if request.method == 'POST':
        aula_id = request.POST.get('aula_id')
        bulk_action = request.POST.get('bulk_action')
        
        if aula_id and bulk_action:
            aula = get_object_or_404(AulaRegistrada, pk=aula_id)
            alunos = turma.get_alunos_enturmados()
            
            if bulk_action == 'all_present':
                # Marcar todos como presentes
                for aluno in alunos:
                    RegistroFrequencia.objects.update_or_create(
                        aula=aula, aluno=aluno,
                        defaults={
                            'situacao': 'PRESENTE',
                            'usuario_registro': request.user
                        }
                    )
                aula.chamada_realizada = True
                aula.save()
                messages.success(request, f'Todos os alunos foram marcados como presentes na aula de {aula.data_aula.strftime("%d/%m/%Y")}.')
            
            elif bulk_action == 'all_absent':
                # Marcar todos como ausentes
                for aluno in alunos:
                    RegistroFrequencia.objects.update_or_create(
                        aula=aula, aluno=aluno,
                        defaults={
                            'situacao': 'AUSENTE',
                            'usuario_registro': request.user
                        }
                    )
                aula.chamada_realizada = True
                aula.save()
                messages.success(request, f'Todos os alunos foram marcados como ausentes na aula de {aula.data_aula.strftime("%d/%m/%Y")}.')
            
            return redirect('avaliacao:turma_diario', turma_id=turma_id)
    
    context = {
        'turma': turma,
        'aulas_sem_chamada': aulas_sem_chamada,
    }
    
    return render(request, 'avaliacao/bulk_attendance.html', context)