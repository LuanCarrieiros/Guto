from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from .models import DiarioEletronico, RegistroChamada, RegistroNota, DiarioOnline, ConteudoAula
from turma.models import Turma, Disciplina, DivisaoPeriodoLetivo, Enturmacao, Avaliacao, AulaRegistrada, NotaAvaliacao
from alunos.models import Aluno


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
    return render(request, 'diario/diario_eletronico_dashboard.html', context)


@login_required
def diario_home(request):
    """Página inicial do diário eletrônico"""
    from django.db.models import Avg, Count
    from turma.models import AulaRegistrada, NotaAvaliacao, RegistroFrequencia

    turmas = Turma.objects.all()

    # Calcular estatísticas reais
    total_alunos = 0
    for turma in turmas:
        total_alunos += turma.get_alunos_enturmados().count()

    # Calcular frequência média real
    try:
        frequencias_totais = RegistroFrequencia.objects.count()
        presencas_totais = RegistroFrequencia.objects.filter(situacao='PRESENTE').count()
        frequencia_media = (presencas_totais / frequencias_totais * 100) if frequencias_totais > 0 else 0
    except:
        frequencia_media = 0

    # Calcular média geral das notas
    try:
        notas = NotaAvaliacao.objects.exclude(nota__isnull=True)
        media_geral = notas.aggregate(Avg('nota'))['nota__avg'] or 0
    except:
        media_geral = 0

    context = {
        'turmas': turmas,
        'total_alunos': total_alunos,
        'frequencia_media': round(frequencia_media, 1),
        'media_geral': round(media_geral, 1),
    }
    return render(request, 'diario/diario_home.html', context)


@login_required
def diario_turma(request, turma_id):
    """Página do diário de uma turma específica"""
    turma = get_object_or_404(Turma, pk=turma_id)

    # Buscar disciplinas que têm relacionamento com esta turma
    disciplinas = turma.get_disciplinas()

    alunos = turma.get_alunos_enturmados()
    total_alunos = alunos.count()

    context = {
        'turma': turma,
        'disciplinas': disciplinas,
        'alunos': alunos,
        'total_alunos': total_alunos,
    }
    return render(request, 'diario/diario_turma.html', context)


@login_required
def diario_disciplina(request, turma_id, disciplina_id):
    """Etapa 2: Seleção de disciplina - Interface do processo em 3 etapas"""
    turma = get_object_or_404(Turma, pk=turma_id)
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)

    # Verificar se a disciplina tem relacionamento com a turma
    tem_relacao = Avaliacao.objects.filter(turma=turma, disciplina=disciplina).exists() or \
                  AulaRegistrada.objects.filter(turma=turma, disciplina=disciplina).exists()

    if not tem_relacao:
        messages.warning(request, f'A disciplina {disciplina.nome} ainda não tem avaliações ou aulas registradas para a turma {turma.nome}.')
        # Não redirecionar, permitir que o usuário crie o relacionamento

    # Buscar divisões do período letivo
    divisoes = DivisaoPeriodoLetivo.objects.filter(ativo=True).order_by('ordem')
    alunos_turma = turma.get_alunos_enturmados()

    # Verificar se há diário eletrônico para esta turma/disciplina
    diario_eletronico, created = DiarioEletronico.objects.get_or_create(
        turma=turma,
        disciplina=disciplina,
        defaults={
            'professor': request.user,
            'data_criacao': timezone.now(),
            'diario_fechado': False
        }
    )

    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisoes': divisoes,
        'alunos_turma': alunos_turma,
        'diario_eletronico': diario_eletronico,
        'total_alunos': alunos_turma.count(),
    }
    return render(request, 'diario/diario_disciplina.html', context)


@login_required
def diario_divisao(request, turma_id, disciplina_id, divisao_id):
    """Etapa 3: Divisão do período - Interface completa do diário"""
    turma = get_object_or_404(Turma, pk=turma_id)
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    divisao = get_object_or_404(DivisaoPeriodoLetivo, pk=divisao_id)

    # Verificar se a disciplina tem relacionamento com a turma
    tem_relacao = Avaliacao.objects.filter(turma=turma, disciplina=disciplina).exists() or \
                  AulaRegistrada.objects.filter(turma=turma, disciplina=disciplina).exists()

    if not tem_relacao:
        messages.warning(request, f'A disciplina {disciplina.nome} ainda não tem avaliações ou aulas registradas para a turma {turma.nome}.')
        # Não redirecionar, permitir que o usuário crie o relacionamento

    # Buscar ou criar diário eletrônico
    diario_eletronico, created = DiarioEletronico.objects.get_or_create(
        turma=turma,
        disciplina=disciplina,
        defaults={
            'professor': request.user,
            'data_criacao': timezone.now(),
            'diario_fechado': False
        }
    )

    # Buscar alunos da turma
    alunos_turma = turma.get_alunos_enturmados()

    # Buscar avaliações da disciplina/divisão
    avaliacoes = Avaliacao.objects.filter(
        turma=turma,
        disciplina=disciplina,
        divisao_periodo=divisao
    ).order_by('data_aplicacao')

    # Buscar registros de notas para cada aluno - usando NotaAvaliacao
    notas_por_aluno = {}
    for aluno in alunos_turma:
        # Buscar notas nas avaliações desta disciplina/divisão
        notas_dict = {}
        for avaliacao in avaliacoes:
            try:
                nota_avaliacao = NotaAvaliacao.objects.get(
                    avaliacao=avaliacao,
                    aluno=aluno
                )
                notas_dict[avaliacao.pk] = nota_avaliacao
            except NotaAvaliacao.DoesNotExist:
                notas_dict[avaliacao.pk] = None

        notas_por_aluno[aluno.pk] = notas_dict

    # Calcular médias dos alunos
    medias_alunos = {}
    for aluno in alunos_turma:
        notas_validas = []
        for avaliacao in avaliacoes:
            nota_obj = notas_por_aluno[aluno.pk].get(avaliacao.pk)
            if nota_obj and nota_obj.nota is not None:
                notas_validas.append(float(nota_obj.nota))

        if notas_validas:
            media = sum(notas_validas) / len(notas_validas)
            medias_alunos[aluno.pk] = media
        else:
            medias_alunos[aluno.pk] = None

    # Buscar registros de chamada
    chamadas = RegistroChamada.objects.filter(
        diario=diario_eletronico,
        data_chamada__isnull=False
    ).order_by('-data_chamada')[:10]  # Últimas 10 chamadas

    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisao': divisao,
        'diario_eletronico': diario_eletronico,
        'alunos_turma': alunos_turma,
        'avaliacoes': avaliacoes,
        'notas_por_aluno': notas_por_aluno,
        'medias_alunos': medias_alunos,
        'chamadas': chamadas,
        'total_alunos': alunos_turma.count(),
    }
    return render(request, 'diario/diario_divisao.html', context)


@login_required
@require_POST
def fechar_diario(request, turma_id, disciplina_id):
    """Fechar o diário eletrônico após validações"""
    turma = get_object_or_404(Turma, pk=turma_id)
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)

    try:
        diario = DiarioEletronico.objects.get(turma=turma, disciplina=disciplina)

        # Validações antes do fechamento
        alunos_turma = turma.get_alunos_enturmados()
        divisoes = DivisaoPeriodoLetivo.objects.filter(ativo=True)

        pendencias = []

        # Verificar se todos os alunos têm notas em todas as divisões
        for divisao in divisoes:
            avaliacoes_divisao = Avaliacao.objects.filter(
                turma=turma,
                disciplina=disciplina,
                divisao_periodo=divisao
            )

            if not avaliacoes_divisao.exists():
                pendencias.append(f'Nenhuma avaliação cadastrada para {divisao.nome}')
                continue

            for aluno in alunos_turma:
                notas_aluno = RegistroNota.objects.filter(
                    diario=diario,
                    aluno=aluno,
                    divisao_periodo=divisao
                )

                if notas_aluno.count() < avaliacoes_divisao.count():
                    pendencias.append(f'Aluno {aluno.nome} - notas pendentes em {divisao.nome}')

        # Se há pendências, retornar erro
        if pendencias:
            messages.error(request, f'Não é possível fechar o diário. Pendências encontradas: {"; ".join(pendencias[:5])}')
            return JsonResponse({'success': False, 'errors': pendencias})

        # Fechar o diário
        diario.diario_fechado = True
        diario.data_fechamento = timezone.now()
        diario.usuario_fechamento = request.user
        diario.save()

        messages.success(request, f'Diário de {disciplina.nome} - {turma.nome} fechado com sucesso!')
        return JsonResponse({'success': True, 'message': 'Diário fechado com sucesso!'})

    except DiarioEletronico.DoesNotExist:
        messages.error(request, 'Diário eletrônico não encontrado.')
        return JsonResponse({'success': False, 'error': 'Diário não encontrado'})


@login_required
@require_POST
def abrir_diario(request, turma_id, disciplina_id):
    """Reabrir o diário eletrônico"""
    turma = get_object_or_404(Turma, pk=turma_id)
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)

    try:
        diario = DiarioEletronico.objects.get(turma=turma, disciplina=disciplina)

        # Reabrir o diário
        diario.diario_fechado = False
        diario.data_reabertura = timezone.now()
        diario.usuario_reabertura = request.user
        diario.save()

        messages.success(request, f'Diário de {disciplina.nome} - {turma.nome} reaberto com sucesso!')
        return JsonResponse({'success': True, 'message': 'Diário reaberto com sucesso!'})

    except DiarioEletronico.DoesNotExist:
        messages.error(request, 'Diário eletrônico não encontrado.')
        return JsonResponse({'success': False, 'error': 'Diário não encontrado'})


@login_required
def gerenciar_avaliacoes_via_diario(request, turma_id):
    """Gerenciar avaliações via diário - redirecionamento para a view do turma app"""
    disciplina_id = request.GET.get('disciplina')

    if disciplina_id:
        # Redirecionar para a view do turma app que já existe
        return redirect('turma:gerenciar_avaliacoes_diario', turma_id=turma_id)
    else:
        messages.error(request, 'Disciplina não especificada.')
        return redirect('diario:turma', turma_id=turma_id)
