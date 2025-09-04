from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg
from django.db import models
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import date, datetime
from .models import (
    Conceito, Turma, Disciplina, LancamentoNota, AtestadoMedico,
    MediaGlobalConceito, RecuperacaoEspecial, ParecerDescritivo,
    AvaliacaoDescritiva, PendenciaAvaliacao, DiarioOnline, ConteudoAula,
    Enturmacao, AulaRegistrada, RegistroFrequencia, TipoAvaliacao,
    Avaliacao, NotaAvaliacao, DivisaoPeriodoLetivo
)
from .forms import TurmaForm, DisciplinaForm, EnturmacaoForm
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
    
    return render(request, 'avaliacao/home.html', context)


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
    
    paginator = Paginator(turmas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'turmas': page_obj,
        'current_filters': {
            'tipo_ensino': tipo_ensino,
            'ano_serie': ano_serie,
            'turno': turno,
        }
    }
    return render(request, 'avaliacao/turmas_list.html', context)


@login_required
def turma_create(request):
    """Cria uma nova turma"""
    # Capturar a página de origem para voltar corretamente
    next_url = request.GET.get('next', 'avaliacao:turmas_list')
    
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            turma = form.save()
            messages.success(request, f'Turma "{turma.nome}" criada com sucesso!')
            
            # Registrar atividade
            AtividadeRecente.objects.create(
                usuario=request.user,
                acao='CREATE',
                modulo='AVALIACAO',
                objeto_nome=turma.nome,
                descricao=f'Criou a turma {turma.nome}'
            )
            
            # Verificar se veio do diário home para redirecionar corretamente
            if 'diario' in request.POST.get('next', ''):
                return redirect('avaliacao:diario_home')
            return redirect('avaliacao:turmas_list')
    else:
        form = TurmaForm()
    
    context = {
        'form': form,
        'next_url': next_url,
        'is_create': True,
        'title': 'Criar Nova Turma'
    }
    
    return render(request, 'avaliacao/turma_form.html', context)


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
                acao='UPDATE',
                modulo='AVALIACAO',
                objeto_nome=turma.nome,
                descricao=f'Editou a turma {turma.nome}'
            )
            
            return redirect('avaliacao:turmas_list')
    else:
        form = TurmaForm(instance=turma)
    
    return render(request, 'avaliacao/turma_form.html', {'form': form, 'turma': turma})


@login_required
def turma_detail(request, pk):
    """Detalhe de uma turma"""
    turma = get_object_or_404(Turma, pk=pk)
    alunos_enturmados = turma.get_alunos_enturmados()
    avaliacoes = Avaliacao.objects.filter(turma=turma).order_by('-data_aplicacao')[:5]
    
    context = {
        'turma': turma,
        'alunos_enturmados': alunos_enturmados,
        'avaliacoes': avaliacoes,
        'total_alunos': alunos_enturmados.count(),
    }
    return render(request, 'avaliacao/turma_detail.html', context)


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
            acao='DELETE',
            modulo='AVALIACAO',
            objeto_nome=nome_turma,
            descricao=f'Excluiu a turma {nome_turma}'
        )
        
        return redirect('avaliacao:turmas_list')
    
    return render(request, 'avaliacao/turma_confirm_delete.html', {'turma': turma})


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
    return render(request, 'avaliacao/disciplinas_list.html', context)


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
                acao='CREATE',
                modulo='AVALIACAO',
                objeto_nome=disciplina.nome,
                descricao=f'Criou a disciplina {disciplina.nome}'
            )
            
            return redirect('avaliacao:disciplinas_list')
    else:
        form = DisciplinaForm()
    
    return render(request, 'avaliacao/disciplina_form.html', {'form': form})


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
                acao='UPDATE',
                modulo='AVALIACAO',
                objeto_nome=disciplina.nome,
                descricao=f'Editou a disciplina {disciplina.nome}'
            )
            
            return redirect('avaliacao:disciplinas_list')
    else:
        form = DisciplinaForm(instance=disciplina)
    
    return render(request, 'avaliacao/disciplina_form.html', {'form': form, 'disciplina': disciplina})


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
            acao='DELETE',
            modulo='AVALIACAO',
            objeto_nome=nome_disciplina,
            descricao=f'Excluiu a disciplina {nome_disciplina}'
        )
        
        return redirect('avaliacao:disciplinas_list')
    
    return render(request, 'avaliacao/disciplina_confirm_delete.html', {'disciplina': disciplina})


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
    return render(request, 'avaliacao/notas_list.html', context)


@login_required
def lancar_notas(request):
    """Formulário para lançar notas"""
    return render(request, 'avaliacao/lancar_notas.html')


@login_required
def avaliacao_create(request):
    """Cria uma nova avaliação"""
    if request.method == 'POST':
        turma_id = request.POST.get('turma')
        disciplina_id = request.POST.get('disciplina')
        tipo_avaliacao_id = request.POST.get('tipo_avaliacao')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        data_aplicacao = request.POST.get('data_aplicacao')
        valor_maximo = request.POST.get('valor_maximo', 10.0)
        peso = request.POST.get('peso', 1.0)
        ativo = request.POST.get('ativo', 'true') == 'true'
        
        try:
            turma = Turma.objects.get(id=turma_id)
            disciplina = Disciplina.objects.get(id=disciplina_id)
            tipo_avaliacao = TipoAvaliacao.objects.get(id=tipo_avaliacao_id)
            
            # Criar ou obter DivisaoPeriodoLetivo
            divisao_periodo, created = DivisaoPeriodoLetivo.objects.get_or_create(
                periodo_letivo=turma.periodo_letivo,
                defaults={
                    'nome': f'1º Bimestre - {turma.periodo_letivo}',
                    'data_inicio': date.today(),
                    'data_fim': date.today(),
                }
            )
            
            avaliacao = Avaliacao.objects.create(
                nome=nome,
                descricao=descricao,
                turma=turma,
                disciplina=disciplina,
                tipo_avaliacao=tipo_avaliacao,
                divisao_periodo=divisao_periodo,
                data_aplicacao=data_aplicacao,
                valor_maximo=float(valor_maximo),
                peso=float(peso),
                ativo=ativo,
                professor=request.user
            )
            
            messages.success(request, f'Avaliação "{nome}" criada com sucesso!')
            
            # Registrar atividade
            AtividadeRecente.objects.create(
                usuario=request.user,
                acao='CREATE',
                modulo='AVALIACAO',
                objeto_nome=nome,
                descricao=f'Criou a avaliação {nome} para a turma {turma.nome}'
            )
            
            return redirect('avaliacao:lancar_notas_avaliacao', avaliacao_id=avaliacao.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar avaliação: {str(e)}')
    
    turmas = Turma.objects.all().order_by('nome')
    disciplinas = Disciplina.objects.all().order_by('nome')
    tipos_avaliacao = TipoAvaliacao.objects.all().order_by('nome')
    
    context = {
        'turmas': turmas,
        'disciplinas': disciplinas,
        'tipos_avaliacao': tipos_avaliacao,
    }
    return render(request, 'avaliacao/avaliacao_form.html', context)


@login_required
def conceitos_list(request):
    """Lista os conceitos disponíveis"""
    conceitos = Conceito.objects.all()
    
    context = {
        'conceitos': conceitos
    }
    return render(request, 'avaliacao/conceitos_list.html', context)


@login_required
def relatorios(request):
    """Dashboard de relatórios"""
    return render(request, 'avaliacao/relatorios.html')


@login_required
def enturmar_alunos(request, pk):
    """Enturma alunos em uma turma específica"""
    turma = get_object_or_404(Turma, pk=pk)
    
    if request.method == 'POST':
        alunos_ids = request.POST.getlist('alunos')
        
        for aluno_id in alunos_ids:
            aluno = get_object_or_404(Aluno, pk=aluno_id)
            
            # Verificar se o aluno já está enturmado
            if not Enturmacao.objects.filter(turma=turma, aluno=aluno, ativo=True).exists():
                Enturmacao.objects.create(
                    turma=turma,
                    aluno=aluno,
                    data_enturmacao=date.today(),
                    ativo=True
                )
        
        messages.success(request, f'{len(alunos_ids)} aluno(s) enturmado(s) com sucesso!')
        return redirect('avaliacao:turma_detail', pk=pk)
    
    # Alunos já enturmados nesta turma
    alunos_enturmados_ids = Enturmacao.objects.filter(
        turma=turma, 
        ativo=True
    ).values_list('aluno_id', flat=True)
    
    # Alunos disponíveis para enturmar
    alunos_disponiveis = Aluno.objects.exclude(
        id__in=alunos_enturmados_ids
    ).order_by('nome')
    
    paginator = Paginator(alunos_disponiveis, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'turma': turma,
        'page_obj': page_obj,
        'alunos': page_obj,
    }
    return render(request, 'avaliacao/enturmar_alunos.html', context)


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
        
        enturmacao.ativo = False
        enturmacao.data_desenturmacao = date.today()
        enturmacao.save()
        
        messages.success(request, f'Aluno {aluno.nome} desenturmado da turma {turma.nome}!')
        return redirect('avaliacao:turma_detail', pk=pk)
    
    context = {
        'turma': turma,
        'aluno': aluno,
    }
    return render(request, 'avaliacao/desenturmar_aluno.html', context)


@login_required
def diario_dashboard(request):
    """Dashboard do diário eletrônico - versão bonita"""
    turmas = Turma.objects.all()
    total_turmas = turmas.count()
    diarios_ativos = total_turmas  # Para agora, consideramos todas as turmas como tendo diários ativos
    
    context = {
        'turmas': turmas,
        'total_turmas': total_turmas,
        'diarios_ativos': diarios_ativos,
    }
    return render(request, 'avaliacao/diario_eletronico_dashboard.html', context)


@login_required
def lancar_notas_avaliacao(request, avaliacao_id):
    """Lança notas para uma avaliação específica"""
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    
    # Obter alunos da turma
    enturmacoes = Enturmacao.objects.filter(
        turma=avaliacao.turma,
        ativo=True
    )
    
    if request.method == 'POST':
        for enturmacao in enturmacoes:
            nota_value = request.POST.get(f'nota_{enturmacao.aluno.id}')
            if nota_value:
                try:
                    nota_value = float(nota_value)
                    
                    # Criar ou atualizar nota
                    nota, created = NotaAvaliacao.objects.get_or_create(
                        avaliacao=avaliacao,
                        aluno=enturmacao.aluno,
                        defaults={'nota': nota_value}
                    )
                    
                    if not created:
                        nota.nota = nota_value
                        nota.save()
                        
                except ValueError:
                    continue
        
        messages.success(request, 'Notas lançadas com sucesso!')
        return redirect('avaliacao:avaliacao_detail', pk=avaliacao.id)
    
    # Obter notas já lançadas
    notas_existentes = NotaAvaliacao.objects.filter(
        avaliacao=avaliacao
    )
    
    notas_dict = {nota.aluno.id: nota.nota for nota in notas_existentes}
    
    context = {
        'avaliacao': avaliacao,
        'enturmacoes': enturmacoes,
        'notas_dict': notas_dict,
    }
    return render(request, 'avaliacao/lancar_notas_avaliacao.html', context)


@login_required
def gerenciar_disciplinas_turma(request, turma_id):
    """Gerencia as disciplinas de uma turma"""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    if request.method == 'POST':
        disciplinas_ids = request.POST.getlist('disciplinas')
        turma.disciplinas.set(disciplinas_ids)
        messages.success(request, 'Disciplinas da turma atualizadas com sucesso!')
        return redirect('avaliacao:turma_detail', pk=turma_id)
    
    todas_disciplinas = Disciplina.objects.all().order_by('nome')
    disciplinas_turma = turma.disciplinas.all()
    
    context = {
        'turma': turma,
        'todas_disciplinas': todas_disciplinas,
        'disciplinas_turma': disciplinas_turma,
    }
    return render(request, 'avaliacao/gerenciar_disciplinas_turma.html', context)


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
        'current_filters': {
            'turma': turma_id,
            'disciplina': disciplina_id,
            'tipo': tipo_id,
            'status': status,
        }
    }
    return render(request, 'avaliacao/avaliacoes_list.html', context)


@login_required
def avaliacao_detail(request, pk):
    """Detalhe de uma avaliação"""
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    notas = NotaAvaliacao.objects.filter(avaliacao=avaliacao)
    
    # Estatísticas
    if notas.exists():
        media = notas.aggregate(Avg('nota'))['nota__avg']
        maior_nota = notas.aggregate(models.Max('nota'))['nota__max']
        menor_nota = notas.aggregate(models.Min('nota'))['nota__min']
    else:
        media = maior_nota = menor_nota = None
    
    context = {
        'avaliacao': avaliacao,
        'notas': notas,
        'estatisticas': {
            'media': media,
            'maior_nota': maior_nota,
            'menor_nota': menor_nota,
            'total_notas': notas.count(),
        }
    }
    return render(request, 'avaliacao/avaliacao_detail.html', context)


@login_required
def avaliacao_edit(request, pk):
    """Edita uma avaliação existente"""
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    
    if request.method == 'POST':
        avaliacao.nome = request.POST.get('nome', avaliacao.nome)
        avaliacao.descricao = request.POST.get('descricao', avaliacao.descricao)
        avaliacao.data_aplicacao = request.POST.get('data_aplicacao', avaliacao.data_aplicacao)
        avaliacao.peso = request.POST.get('peso', avaliacao.peso)
        
        avaliacao.save()
        
        messages.success(request, f'Avaliação "{avaliacao.nome}" editada com sucesso!')
        
        # Registrar atividade
        AtividadeRecente.objects.create(
            usuario=request.user,
            acao='UPDATE',
            modulo='AVALIACAO',
            objeto_nome=avaliacao.nome,
            descricao=f'Editou a avaliação {avaliacao.nome}'
        )
        
        return redirect('avaliacao:avaliacao_detail', pk=pk)
    
    context = {
        'avaliacao': avaliacao,
    }
    return render(request, 'avaliacao/avaliacao_edit.html', context)


@login_required
def avaliacao_delete(request, pk):
    """Exclui uma avaliação"""
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    
    if request.method == 'POST':
        nome_avaliacao = avaliacao.nome
        avaliacao.delete()
        messages.success(request, f'Avaliação "{nome_avaliacao}" excluída com sucesso!')
        
        # Registrar atividade
        AtividadeRecente.objects.create(
            usuario=request.user,
            acao='DELETE',
            modulo='AVALIACAO',
            objeto_nome=nome_avaliacao,
            descricao=f'Excluiu a avaliação {nome_avaliacao}'
        )
        
        return redirect('avaliacao:avaliacoes_list')
    
    return render(request, 'avaliacao/avaliacao_confirm_delete.html', {'avaliacao': avaliacao})


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
def diario_home(request):
    """Página inicial do Diário Eletrônico - Seleção de turma"""
    turmas = Turma.objects.all().order_by('nome')
    
    context = {
        'turmas': turmas,
        'page_title': 'Diário Eletrônico'
    }
    
    return render(request, 'avaliacao/diario_home.html', context)


@login_required
def diario_turma(request, turma_id):
    """Interface principal do Diário para uma turma específica"""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Buscar alunos da turma
    alunos = Aluno.objects.filter(
        enturmacoes__turma=turma,
        enturmacoes__ativo=True
    ).order_by('nome')
    
    # Estatísticas da turma
    total_alunos = alunos.count()
    
    context = {
        'turma': turma,
        'alunos': alunos,
        'total_alunos': total_alunos,
        'page_title': f'Diário - {turma.nome}'
    }
    
    return render(request, 'avaliacao/diario_turma.html', context)


@login_required
def fazer_chamada(request, turma_id):
    """Interface para fazer chamada de presença"""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Buscar alunos da turma
    alunos = Aluno.objects.filter(
        enturmacoes__turma=turma,
        enturmacoes__ativo=True
    ).order_by('nome')
    
    if request.method == 'POST':
        # Processar dados da chamada
        data_aula = request.POST.get('data_aula', date.today())
        
        for aluno in alunos:
            presente = request.POST.get(f'presente_{aluno.pk}') == 'on'
            
            # Registrar ou atualizar presença
            registro, created = RegistroFrequencia.objects.get_or_create(
                aluno=aluno,
                turma=turma,
                data=data_aula,
                defaults={'presente': presente}
            )
            
            if not created:
                registro.presente = presente
                registro.save()
        
        messages.success(request, 'Chamada registrada com sucesso!')
        return redirect('avaliacao:diario_turma', turma_id=turma_id)
    
    context = {
        'turma': turma,
        'alunos': alunos,
        'data_hoje': date.today(),
        'page_title': f'Chamada - {turma.nome}'
    }
    
    return render(request, 'avaliacao/fazer_chamada_diario.html', context)


@login_required
def lancar_notas_diario(request, turma_id):
    """Interface para lançar notas no diário"""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Buscar alunos da turma
    alunos = Aluno.objects.filter(
        enturmacoes__turma=turma,
        enturmacoes__ativo=True
    ).order_by('nome')
    
    # Buscar avaliações da turma
    avaliacoes = Avaliacao.objects.filter(turma=turma).order_by('-data_criacao')
    
    # Buscar notas existentes
    notas_existentes = NotaAvaliacao.objects.filter(
        avaliacao__turma=turma,
        aluno__in=alunos
    ).select_related('avaliacao', 'aluno')
    
    # Adicionar notas aos alunos
    alunos_list = list(alunos)
    notas_dict = {}
    for nota in notas_existentes:
        if nota.aluno.id not in notas_dict:
            notas_dict[nota.aluno.id] = []
        notas_dict[nota.aluno.id].append(nota)
    
    # Adicionar as notas como atributo aos alunos
    for aluno in alunos_list:
        aluno.notas_existentes = notas_dict.get(aluno.pk, [])
    
    # Handle AJAX request for saving grades
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        import json
        try:
            data = json.loads(request.body)
            aluno_id = data.get('aluno_id')
            avaliacao_id = data.get('avaliacao_id')
            nota_valor = data.get('nota')
            
            aluno = get_object_or_404(Aluno, id=aluno_id)
            avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
            
            # Criar ou atualizar a nota
            nota_obj, created = NotaAvaliacao.objects.get_or_create(
                aluno=aluno,
                avaliacao=avaliacao,
                defaults={'nota': nota_valor}
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
            return JsonResponse({
                'success': False,
                'message': f'Erro ao salvar nota: {str(e)}'
            })
    
    context = {
        'turma': turma,
        'alunos': alunos_list,
        'avaliacoes': avaliacoes,
        'notas_dict': notas_dict,
        'page_title': f'Lançar Notas - {turma.nome}'
    }
    
    return render(request, 'avaliacao/lancar_notas_diario.html', context)