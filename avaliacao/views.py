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
            context = {
                'turma': turma,
                'alunos_ja_enturmados': alunos_ja_enturmados,
                'alunos_ids': alunos_ids,
                'mostrar_confirmacao': True,
            }
            return render(request, 'avaliacao/enturmar_alunos.html', context)
        
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
        return redirect('avaliacao:turma_detail', pk=pk)
    
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
    
    context = {
        'turma': turma,
        'alunos_disponiveis': alunos_disponiveis,
        'vagas_disponiveis': vagas_disponiveis,
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
        return redirect('avaliacao:turma_detail', pk=turma.pk)
    
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
                        defaults={
                            'nota': nota_value,
                            'usuario_lancamento': request.user
                        }
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
        
        # Remover diários eletrônicos existentes
        DiarioEletronico.objects.filter(turma=turma).delete()
        
        # Criar novos diários eletrônicos para as disciplinas selecionadas
        for disciplina_id in disciplinas_ids:
            disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
            DiarioEletronico.objects.create(
                turma=turma,
                disciplina=disciplina,
                periodo_letivo=turma.periodo_letivo,
                usuario_criacao=request.user
            )
        
        messages.success(request, f'{len(disciplinas_ids)} disciplina(s) vinculada(s) à turma com sucesso!')
        return redirect('avaliacao:turma_detail', pk=turma_id)
    
    todas_disciplinas = Disciplina.objects.all().order_by('nome')
    # Buscar disciplinas que têm diários para esta turma
    disciplinas_turma = Disciplina.objects.filter(
        diarios_eletronicos__turma=turma
    ).distinct().order_by('nome')
    
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
    
    # Buscar disciplinas ativas do sistema
    disciplinas = Disciplina.objects.filter(ativo=True).order_by('nome')
    
    # Estatísticas da turma
    total_alunos = alunos.count()
    
    context = {
        'turma': turma,
        'alunos': alunos,
        'disciplinas': disciplinas,
        'total_alunos': total_alunos,
        'page_title': f'Diário - {turma.nome}'
    }
    
    return render(request, 'avaliacao/diario/diario_turma.html', context)


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
            return redirect('diario:chamada', turma_id=turma_id)
        
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
        return redirect('diario:turma', turma_id=turma_id)
    
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'alunos': alunos_list,  # Usar lista com status
        'data_hoje': date.today(),
        'data_atual': data_chamada.strftime('%Y-%m-%d'),  # Data para o input
        'page_title': f'Chamada - {disciplina.nome} - {turma.nome}'
    }
    
    return render(request, 'avaliacao/diario/fazer_chamada_diario.html', context)


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
        'alunos': alunos_list,
        'avaliacoes': avaliacoes,
        'notas_dict': notas_dict,
        'tipos_avaliacao': tipos_avaliacao,
        'page_title': f'Lançar Notas - {turma.nome}'
    }
    
    return render(request, 'avaliacao/diario/lancar_notas_diario.html', context)


@login_required
def gerenciar_avaliacoes_diario(request, turma_id):
    """Gerencia avaliações no contexto do diário"""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Obter disciplina da URL
    disciplina_id = request.GET.get('disciplina')
    if not disciplina_id:
        messages.error(request, 'Selecione uma disciplina para gerenciar avaliações.')
        return redirect('diario:notas', turma_id=turma_id)
    
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    
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
                
                # Obter uma divisão de período padrão
                divisao_periodo = DivisaoPeriodoLetivo.objects.first()
                if not divisao_periodo:
                    # Criar uma divisão padrão se não existir
                    divisao_periodo = DivisaoPeriodoLetivo.objects.create(
                        nome="1º Bimestre",
                        tipo_divisao="BIMESTRE",
                        ano_letivo=turma.periodo_letivo,
                        data_inicio=date.today(),
                        data_fim=date.today(),
                        usuario_criacao=request.user
                    )
                
                avaliacao = Avaliacao.objects.create(
                    nome=nome,
                    descricao=descricao,
                    tipo_avaliacao=tipo_avaliacao,
                    turma=turma,
                    disciplina=disciplina,
                    divisao_periodo=divisao_periodo,
                    peso=float(peso),
                    data_aplicacao=data_aplicacao,
                    professor=request.user
                )
                
                messages.success(request, f'Avaliação "{nome}" criada com sucesso!')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': f'Avaliação "{nome}" criada com sucesso!'})
                return redirect(f'/diario/disciplina/avaliacoes/turma/{turma_id}/?disciplina={disciplina_id}')
                
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
        'avaliacoes': avaliacoes,
        'tipos_avaliacao': tipos_avaliacao,
        'page_title': f'Avaliações - {disciplina.nome} - {turma.nome}'
    }
    
    return render(request, 'avaliacao/diario/gerenciar_avaliacoes_diario.html', context)


def visualizar_avaliacoes_diario(request, turma_id):
    """Visualiza avaliações no contexto do diário (Espelho do Diário)"""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Obter disciplina da URL
    disciplina_id = request.GET.get('disciplina')
    if not disciplina_id:
        messages.error(request, 'Selecione uma disciplina para visualizar avaliações.')
        return redirect('diario:notas', turma_id=turma_id)
    
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    
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
        'avaliacoes': avaliacoes,
        'page_title': f'Espelho do Diário - {disciplina.nome} - {turma.nome}'
    }
    
    return render(request, 'avaliacao/diario/visualizar_avaliacoes_diario.html', context)


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
                return redirect(f'/diario/disciplina/avaliacoes/turma/{avaliacao.turma.pk}/?disciplina={avaliacao.disciplina.pk}')
                
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
    
    return render(request, 'avaliacao/diario/editar_avaliacao_diario.html', context)


@login_required
def excluir_avaliacao_diario(request, avaliacao_id):
    """Exclui avaliação no contexto do diário"""
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    turma_id = avaliacao.turma.pk
    disciplina_id = avaliacao.disciplina.pk
    nome_avaliacao = avaliacao.nome
    
    try:
        avaliacao.delete()
        success_msg = f'Avaliação "{nome_avaliacao}" excluída com sucesso!'
        messages.success(request, success_msg)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': success_msg})
    except Exception as e:
        error_msg = f'Erro ao excluir avaliação: {str(e)}'
        messages.error(request, error_msg)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
    
    return redirect(f'/diario/disciplina/avaliacoes/turma/{turma_id}/?disciplina={disciplina_id}')