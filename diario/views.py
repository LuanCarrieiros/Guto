"""
Diário eletrônico.

Fluxo: Turma → Disciplina → Período (bimestre) → ações (chamada, notas, avaliações,
pareceres). A recuperação especial é lançada por disciplina, ao final do ano.
Quando o diário de uma disciplina está fechado, nenhuma alteração é aceita.
"""
import json
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from turma import relatorios
from turma.forms import AvaliacaoDiarioForm
from turma.models import (
    AulaRegistrada, Avaliacao, AvaliacaoDescritiva, Conceito, Disciplina, DivisaoPeriodoLetivo, NotaAvaliacao,
    RecuperacaoEspecial, RegistroFrequencia, TipoAvaliacao, Turma,
)
from .acesso import exigir_acesso, filtrar_disciplinas, filtrar_turmas
from .models import DiarioEletronico


# ============================== AUXILIARES ==============================

def obter_diario(turma, disciplina, usuario=None):
    """Diário da disciplina na turma (criado na primeira vez que é aberto)."""
    diario, _ = DiarioEletronico.objects.get_or_create(turma=turma, disciplina=disciplina)
    return diario


def carregar_contexto(request, turma_id, disciplina_id, divisao_id=None):
    """Busca turma/disciplina/período e garante que o usuário pode abrir este diário."""
    turma = get_object_or_404(Turma, pk=turma_id)
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    exigir_acesso(request.user, turma, disciplina)
    divisao = get_object_or_404(
        DivisaoPeriodoLetivo, pk=divisao_id, periodo_letivo=turma.periodo_letivo
    ) if divisao_id else None
    return turma, disciplina, divisao


def url_divisao(turma, disciplina, divisao, nome='divisao'):
    return reverse(f'diario:{nome}', args=[turma.pk, disciplina.pk, divisao.pk])


def diario_fechado(request, diario, destino):
    """Retorna um redirecionamento (ou JSON) se o diário estiver fechado; senão None."""
    if not diario.diario_fechado:
        return None
    mensagem = 'Este diário está fechado. Reabra-o para fazer alterações.'
    if request.headers.get('Content-Type') == 'application/json' or \
            request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': mensagem, 'error': mensagem}, status=403)
    messages.error(request, mensagem)
    return redirect(destino)


# ============================== NAVEGAÇÃO ==============================

@login_required
def diario_home(request):
    """Página inicial do diário eletrônico"""
    turmas = filtrar_turmas(request.user, Turma.objects.annotate(
        total_alunos_ativos=Count('enturmacoes', filter=Q(enturmacoes__ativo=True))
    ).order_by('-periodo_letivo', 'nome'))
    total_registros = RegistroFrequencia.objects.count()
    presencas = RegistroFrequencia.objects.exclude(situacao='AUSENTE').count()
    media_geral = NotaAvaliacao.objects.filter(nota__isnull=False).aggregate(media=Avg('nota'))['media'] or 0

    context = {
        'turmas': turmas,
        'total_alunos': sum(t.total_alunos_ativos for t in turmas),
        'frequencia_media': round(presencas * 100 / total_registros, 1) if total_registros else 0,
        'media_geral': round(float(media_geral), 1),
    }
    return render(request, 'diario/diario_home.html', context)


@login_required
def diario_turma(request, turma_id):
    """Etapa 1: disciplinas da turma"""
    turma = get_object_or_404(Turma, pk=turma_id)
    exigir_acesso(request.user, turma)
    alunos = turma.get_alunos_enturmados()
    divisoes = list(DivisaoPeriodoLetivo.objects.filter(ativo=True, periodo_letivo=turma.periodo_letivo))
    avaliacoes = Avaliacao.objects.filter(turma=turma, ativo=True)
    disciplinas = list(filtrar_disciplinas(request.user, turma, turma.get_disciplinas()))
    for disciplina in disciplinas:
        da_disciplina = avaliacoes.filter(disciplina=disciplina)
        com_avaliacao = da_disciplina.values('divisao_periodo').distinct().count()
        disciplina.divisoes_count = len(divisoes)
        disciplina.avaliacoes_count = da_disciplina.count()
        disciplina.progresso = f'{round(com_avaliacao * 100 / len(divisoes))}%' if divisoes else '0%'
        disciplina.professor = obter_diario(turma, disciplina).professor
    context = {
        'turma': turma,
        'disciplinas': disciplinas,
        'alunos': alunos,
        'total_alunos': alunos.count(),
    }
    return render(request, 'diario/diario_turma.html', context)


@login_required
def diario_disciplina(request, turma_id, disciplina_id):
    """Etapa 2: escolha do período (bimestre)"""
    turma, disciplina, _ = carregar_contexto(request, turma_id, disciplina_id)
    alunos_turma = turma.get_alunos_enturmados()
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisoes': DivisaoPeriodoLetivo.objects.filter(
            ativo=True, periodo_letivo=turma.periodo_letivo
        ).order_by('ordem'),
        'alunos_turma': alunos_turma,
        'diario_eletronico': obter_diario(turma, disciplina, request.user),
        'total_alunos': alunos_turma.count(),
    }
    context['professor'] = context['diario_eletronico'].professor
    return render(request, 'diario/diario_disciplina.html', context)


@login_required
def diario_divisao(request, turma_id, disciplina_id, divisao_id):
    """Etapa 3: painel do período com notas, médias e chamadas"""
    turma, disciplina, divisao = carregar_contexto(request, turma_id, disciplina_id, divisao_id)
    alunos_turma = list(turma.get_alunos_enturmados())
    avaliacoes = list(Avaliacao.objects.filter(
        turma=turma, disciplina=disciplina, divisao_periodo=divisao
    ).order_by('data_aplicacao'))

    # Espelho: uma linha por aluno, uma coluna por avaliação (sempre pelo ID do aluno)
    notas = {(n.aluno_id, n.avaliacao_id): n for n in
             NotaAvaliacao.objects.filter(avaliacao__in=avaliacoes).select_related('avaliacao')}
    espelho = []
    for aluno in alunos_turma:
        do_aluno = [notas.get((aluno.pk, a.pk)) for a in avaliacoes]
        espelho.append({
            'aluno': aluno,
            'notas': do_aluno,
            'media': relatorios.media_ponderada([n for n in do_aluno if n is not None]),
        })

    aulas = AulaRegistrada.objects.filter(
        turma=turma, disciplina=disciplina,
        data_aula__range=(divisao.data_inicio, divisao.data_fim),
    ).annotate(
        presentes=Count('frequencias', filter=~Q(frequencias__situacao='AUSENTE')),
        total=Count('frequencias'),
    ).order_by('-data_aula')

    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisao': divisao,
        'diario_eletronico': obter_diario(turma, disciplina, request.user),
        'professor': obter_diario(turma, disciplina).professor,
        'alunos_turma': alunos_turma,
        'avaliacoes': avaliacoes,
        'espelho': espelho,
        'media_aprovacao': relatorios.criterios_aprovacao()['media'],
        'chamadas': aulas[:10],
        'total_alunos': len(alunos_turma),
    }
    return render(request, 'diario/diario_divisao.html', context)


# ============================== CHAMADA ==============================

@login_required
def fazer_chamada(request, turma_id, disciplina_id, divisao_id):
    """Registro de presença dos alunos em uma data"""
    turma, disciplina, divisao = carregar_contexto(request, turma_id, disciplina_id, divisao_id)
    diario = obter_diario(turma, disciplina, request.user)
    voltar = url_divisao(turma, disciplina, divisao)
    alunos = list(turma.get_alunos_enturmados())

    data_param = request.POST.get('data_aula') or request.GET.get('data')
    try:
        data_chamada = datetime.strptime(data_param, '%Y-%m-%d').date() if data_param else date.today()
    except ValueError:
        data_chamada = date.today()

    if request.method == 'POST':
        bloqueio = diario_fechado(request, diario, voltar)
        if bloqueio:
            return bloqueio
        if data_chamada > date.today():
            messages.error(request, 'Não é possível registrar chamada para uma data futura.')
            return redirect(f"{request.path}?data={data_chamada:%Y-%m-%d}")
        with transaction.atomic():
            aula = AulaRegistrada.objects.filter(
                turma=turma, disciplina=disciplina, data_aula=data_chamada
            ).order_by('horario_inicio').first() or AulaRegistrada.objects.create(
                turma=turma, disciplina=disciplina, data_aula=data_chamada, professor=request.user,
                horario_inicio=time(7, 0), horario_fim=time(12, 0),
                conteudo_programatico=f'Chamada de {data_chamada:%d/%m/%Y}',
            )
            for aluno in alunos:
                presente = request.POST.get(f'toggle_{aluno.codigo}', 'presente') == 'presente'
                RegistroFrequencia.objects.update_or_create(
                    aula=aula, aluno=aluno,
                    defaults={'situacao': 'PRESENTE' if presente else 'AUSENTE', 'usuario_registro': request.user},
                )
            aula.chamada_realizada = True
            aula.save(update_fields=['chamada_realizada'])
        messages.success(request, f'Chamada do dia {data_chamada:%d/%m/%Y} registrada com sucesso!')
        return redirect(voltar)

    aula = AulaRegistrada.objects.filter(
        turma=turma, disciplina=disciplina, data_aula=data_chamada
    ).order_by('horario_inicio').first()
    situacoes = dict(aula.frequencias.values_list('aluno_id', 'situacao')) if aula else {}
    for aluno in alunos:
        aluno.status_atual = situacoes.get(aluno.pk, 'PRESENTE')

    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisao': divisao,
        'diario_eletronico': diario,
        'alunos': alunos,
        'data_hoje': date.today(),
        'data_atual': data_chamada.strftime('%Y-%m-%d'),
        'page_title': f'Chamada - {disciplina.nome} - {turma.nome}',
    }
    return render(request, 'diario/fazer_chamada_diario.html', context)


# ============================== NOTAS ==============================

def _salvar_nota_json(request, turma, disciplina, divisao, alunos_ids):
    try:
        dados = json.loads(request.body)
        avaliacao = Avaliacao.objects.get(
            pk=dados.get('avaliacao_id'), turma=turma, disciplina=disciplina, divisao_periodo=divisao,
        )
        aluno_id = int(dados.get('aluno_id'))
        nota = Decimal(str(dados.get('nota')).replace(',', '.'))
    except (ValueError, TypeError, InvalidOperation, json.JSONDecodeError):
        return JsonResponse({'success': False, 'message': 'Dados inválidos.'}, status=400)
    except Avaliacao.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Avaliação não encontrada neste período.'}, status=404)

    conceito = None
    if dados.get('conceito_id'):
        conceito = Conceito.objects.filter(pk=dados['conceito_id'], ativo=True).first()
        if conceito is None:
            return JsonResponse({'success': False, 'message': 'Conceito inválido.'}, status=400)
        # A nota equivalente ao conceito (escala 0–10) entra no cálculo das médias
        nota = (conceito.valor_numerico * avaliacao.valor_maximo / Decimal('10')).quantize(Decimal('0.01'))

    if aluno_id not in alunos_ids:
        return JsonResponse({'success': False, 'message': 'O aluno não pertence a esta turma.'}, status=400)
    if nota < 0 or nota > avaliacao.valor_maximo:
        return JsonResponse({
            'success': False, 'message': f'A nota deve estar entre 0 e {avaliacao.valor_maximo}.',
        }, status=400)

    NotaAvaliacao.objects.update_or_create(
        avaliacao=avaliacao, aluno_id=aluno_id,
        defaults={
            'nota': nota,
            'conceito': conceito,
            'ausente': False,
            'observacoes': (dados.get('observacao') or '').strip() or None,
            'usuario_lancamento': request.user,
        },
    )
    total_alunos = len(alunos_ids)
    lancadas = avaliacao.notas.filter(nota__isnull=False).count()
    if avaliacao.notas_lancadas != (lancadas >= total_alunos):
        avaliacao.notas_lancadas = lancadas >= total_alunos
        avaliacao.save(update_fields=['notas_lancadas'])
    return JsonResponse({'success': True, 'message': f'Nota {nota} salva com sucesso!', 'nota': float(nota)})


@login_required
def lancar_notas(request, turma_id, disciplina_id, divisao_id):
    """Lançamento das notas das avaliações do período"""
    turma, disciplina, divisao = carregar_contexto(request, turma_id, disciplina_id, divisao_id)
    diario = obter_diario(turma, disciplina, request.user)
    alunos = list(turma.get_alunos_enturmados())

    if request.method == 'POST':
        bloqueio = diario_fechado(request, diario, url_divisao(turma, disciplina, divisao))
        if bloqueio:
            return bloqueio
        return _salvar_nota_json(request, turma, disciplina, divisao, {a.pk for a in alunos})

    avaliacoes = list(Avaliacao.objects.filter(
        turma=turma, disciplina=disciplina, divisao_periodo=divisao, ativo=True,
    ).annotate(
        notas_existentes_count=Count('notas', filter=Q(notas__nota__isnull=False))
    ).order_by('data_aplicacao', 'nome'))

    notas_dict = {}
    for nota in NotaAvaliacao.objects.filter(avaliacao__in=avaliacoes).select_related('avaliacao'):
        notas_dict.setdefault(nota.aluno_id, []).append(nota)
    for aluno in alunos:
        aluno.notas_existentes = notas_dict.get(aluno.pk, [])

    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisao': divisao,
        'diario_eletronico': diario,
        'alunos': alunos,
        'avaliacoes': avaliacoes,
        'notas_dict': notas_dict,
        'tipos_avaliacao': TipoAvaliacao.objects.filter(ativo=True).order_by('nome'),
        'conceitos': Conceito.objects.filter(ativo=True) if disciplina.avalia_por_conceito else None,
        'page_title': f'Lançar Notas - {turma.nome}',
    }
    return render(request, 'diario/lancar_notas_diario.html', context)


# ============================== AVALIAÇÕES ==============================

def _contexto_avaliacoes(turma, disciplina, divisao):
    return Avaliacao.objects.filter(
        turma=turma, disciplina=disciplina, divisao_periodo=divisao,
    ).select_related('tipo_avaliacao').annotate(total_notas_lancadas=Count('notas')).order_by('data_aplicacao', 'nome')


@login_required
def gerenciar_avaliacoes(request, turma_id, disciplina_id, divisao_id):
    """Cadastro das avaliações do período"""
    turma, disciplina, divisao = carregar_contexto(request, turma_id, disciplina_id, divisao_id)
    diario = obter_diario(turma, disciplina, request.user)
    form_data = {}

    if request.method == 'POST':
        bloqueio = diario_fechado(request, diario, request.path)
        if bloqueio:
            return bloqueio
        form = AvaliacaoDiarioForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.turma, avaliacao.disciplina, avaliacao.divisao_periodo = turma, disciplina, divisao
            avaliacao.professor = request.user
            avaliacao.save()
            mensagem = f'Avaliação "{avaliacao.nome}" criada com sucesso!'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': mensagem})
            messages.success(request, mensagem)
            return redirect(request.path)
        erros = '; '.join(e for lista in form.errors.values() for e in lista)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': erros}, status=400)
        messages.error(request, f'Não foi possível criar a avaliação: {erros}')
        form_data = request.POST

    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisao': divisao,
        'diario_eletronico': diario,
        'avaliacoes': _contexto_avaliacoes(turma, disciplina, divisao),
        'tipos_avaliacao': TipoAvaliacao.objects.filter(ativo=True).order_by('nome'),
        'form_data': form_data,
        'page_title': f'Avaliações - {disciplina.nome} - {turma.nome}',
    }
    return render(request, 'diario/gerenciar_avaliacoes_diario.html', context)


@login_required
def visualizar_avaliacoes(request, turma_id, disciplina_id, divisao_id):
    """Espelho do diário: avaliações do período e seu andamento"""
    turma, disciplina, divisao = carregar_contexto(request, turma_id, disciplina_id, divisao_id)
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'divisao': divisao,
        'avaliacoes': _contexto_avaliacoes(turma, disciplina, divisao),
        'page_title': f'Espelho do Diário - {disciplina.nome} - {turma.nome}',
    }
    return render(request, 'diario/visualizar_avaliacoes_diario.html', context)


@login_required
def editar_avaliacao(request, avaliacao_id):
    """Edição de uma avaliação"""
    avaliacao = get_object_or_404(Avaliacao.objects.select_related('turma', 'disciplina', 'divisao_periodo'), pk=avaliacao_id)
    exigir_acesso(request.user, avaliacao.turma, avaliacao.disciplina)
    voltar = url_divisao(avaliacao.turma, avaliacao.disciplina, avaliacao.divisao_periodo, 'gerenciar_avaliacoes')
    diario = obter_diario(avaliacao.turma, avaliacao.disciplina, request.user)
    form_data = {}

    if request.method == 'POST':
        bloqueio = diario_fechado(request, diario, voltar)
        if bloqueio:
            return bloqueio
        form = AvaliacaoDiarioForm(request.POST, instance=avaliacao)
        if form.is_valid():
            form.save()
            messages.success(request, f'Avaliação "{avaliacao.nome}" atualizada com sucesso!')
            return redirect(voltar)
        messages.error(request, '; '.join(e for lista in form.errors.values() for e in lista))
        form_data = {
            'nome': request.POST.get('nome'), 'descricao': request.POST.get('descricao'),
            'tipo_avaliacao_id': request.POST.get('tipo_avaliacao'), 'peso': request.POST.get('peso'),
            'data_aplicacao': request.POST.get('data_aplicacao'),
        }

    context = {
        'avaliacao': avaliacao,
        'form_data': form_data,
        'turma': avaliacao.turma,
        'disciplina': avaliacao.disciplina,
        'divisao': avaliacao.divisao_periodo,
        'tipos_avaliacao': TipoAvaliacao.objects.order_by('nome'),
        'page_title': f'Editar Avaliação - {avaliacao.nome}',
    }
    return render(request, 'diario/editar_avaliacao_diario.html', context)


@login_required
@require_POST
def excluir_avaliacao(request, avaliacao_id):
    """Exclusão de uma avaliação (somente via POST)"""
    avaliacao = get_object_or_404(Avaliacao.objects.select_related('turma', 'disciplina', 'divisao_periodo'), pk=avaliacao_id)
    exigir_acesso(request.user, avaliacao.turma, avaliacao.disciplina)
    destino = url_divisao(avaliacao.turma, avaliacao.disciplina, avaliacao.divisao_periodo, 'gerenciar_avaliacoes')
    bloqueio = diario_fechado(request, obter_diario(avaliacao.turma, avaliacao.disciplina), destino)
    if bloqueio:
        return bloqueio
    nome = avaliacao.nome
    avaliacao.delete()
    mensagem = f'Avaliação "{nome}" excluída com sucesso!'
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': mensagem})
    messages.success(request, mensagem)
    return redirect(destino)


# ============================== PARECERES E RECUPERAÇÃO ==============================

@login_required
def pareceres(request, turma_id, disciplina_id, divisao_id):
    """Parecer descritivo de cada aluno no período (exibido no boletim)"""
    turma, disciplina, divisao = carregar_contexto(request, turma_id, disciplina_id, divisao_id)
    diario = obter_diario(turma, disciplina, request.user)
    alunos = list(turma.get_alunos_enturmados())
    existentes = {
        p.aluno_id: p for p in AvaliacaoDescritiva.objects.filter(turma=turma, disciplina=disciplina, divisao_periodo=divisao)
    }

    if request.method == 'POST':
        bloqueio = diario_fechado(request, diario, request.path)
        if bloqueio:
            return bloqueio
        salvos = 0
        with transaction.atomic():
            for aluno in alunos:
                texto = request.POST.get(f'parecer_{aluno.pk}', '').strip()
                if texto:
                    AvaliacaoDescritiva.objects.update_or_create(
                        turma=turma, aluno=aluno, divisao_periodo=divisao, disciplina=disciplina,
                        defaults={'observacoes_descricao_global': texto, 'usuario_lancamento': request.user},
                    )
                    salvos += 1
                elif aluno.pk in existentes:
                    existentes[aluno.pk].delete()
        messages.success(request, f'{salvos} parecer(es) salvo(s).')
        return redirect(url_divisao(turma, disciplina, divisao))

    linhas = [{'aluno': a, 'texto': existentes[a.pk].observacoes_descricao_global if a.pk in existentes else ''}
              for a in alunos]
    context = {
        'turma': turma, 'disciplina': disciplina, 'divisao': divisao,
        'diario_eletronico': diario, 'linhas': linhas,
    }
    return render(request, 'diario/pareceres.html', context)


@login_required
def recuperacao(request, turma_id, disciplina_id):
    """Recuperação especial: nota final para alunos abaixo da média na disciplina"""
    turma, disciplina, _ = carregar_contexto(request, turma_id, disciplina_id)
    diario = obter_diario(turma, disciplina, request.user)
    criterios = relatorios.criterios_aprovacao()
    existentes = {r.aluno_id: r for r in RecuperacaoEspecial.objects.filter(turma=turma, disciplina=disciplina)}

    linhas = []
    for aluno in turma.get_alunos_enturmados():
        media = relatorios.media_disciplina(turma, aluno, disciplina)
        if aluno.pk in existentes or (media is not None and media < criterios['media']):
            linhas.append({'aluno': aluno, 'media': media, 'registro': existentes.get(aluno.pk)})

    if request.method == 'POST':
        bloqueio = diario_fechado(request, diario, request.path)
        if bloqueio:
            return bloqueio
        erros = []
        with transaction.atomic():
            for linha in linhas:
                aluno = linha['aluno']
                nao_optou = request.POST.get(f'nao_optou_{aluno.pk}') == 'on'
                valor = request.POST.get(f'nota_{aluno.pk}', '').strip().replace(',', '.')
                if not valor and not nao_optou:
                    if linha['registro']:
                        linha['registro'].delete()
                    continue
                nota = None
                if valor and not nao_optou:
                    try:
                        nota = Decimal(valor)
                    except InvalidOperation:
                        erros.append(aluno.nome)
                        continue
                    if not 0 <= nota <= 10:
                        erros.append(aluno.nome)
                        continue
                RecuperacaoEspecial.objects.update_or_create(
                    turma=turma, disciplina=disciplina, aluno=aluno,
                    defaults={
                        'nota_atual': Decimal(str(round(linha['media'] or 0, 2))),
                        'nota_recuperacao': nota,
                        'nao_optou': nao_optou,
                        'usuario_lancamento': request.user,
                    },
                )
        if erros:
            messages.error(request, f'Notas inválidas (use 0 a 10) para: {", ".join(erros)}.')
        else:
            messages.success(request, 'Recuperação especial registrada.')
        return redirect(request.path)

    context = {
        'turma': turma, 'disciplina': disciplina, 'diario_eletronico': diario,
        'linhas': linhas, 'criterios': criterios,
    }
    return render(request, 'diario/recuperacao.html', context)


# ============================== FECHAMENTO ==============================

@login_required
@require_POST
def fechar_diario(request, turma_id, disciplina_id):
    """Fecha o diário da disciplina, desde que todas as notas estejam lançadas"""
    turma, disciplina, _ = carregar_contexto(request, turma_id, disciplina_id)
    diario = obter_diario(turma, disciplina, request.user)
    alunos = list(turma.get_alunos_enturmados())
    pendencias = []

    for divisao in DivisaoPeriodoLetivo.objects.filter(ativo=True, periodo_letivo=turma.periodo_letivo).order_by('ordem'):
        avaliacoes = Avaliacao.objects.filter(turma=turma, disciplina=disciplina, divisao_periodo=divisao, ativo=True)
        if not avaliacoes.exists():
            pendencias.append(f'Nenhuma avaliação cadastrada para {divisao.nome}')
            continue
        lancadas = dict(
            NotaAvaliacao.objects.filter(avaliacao__in=avaliacoes)
            .filter(Q(nota__isnull=False) | Q(ausente=True) | Q(dispensado=True))
            .values('aluno').annotate(total=Count('id')).values_list('aluno', 'total')
        )
        total = avaliacoes.count()
        for aluno in alunos:
            if lancadas.get(aluno.pk, 0) < total:
                pendencias.append(f'{aluno.nome} - notas pendentes em {divisao.nome}')

    if pendencias:
        messages.error(request, f'Não é possível fechar o diário. Pendências: {"; ".join(pendencias[:5])}')
        return JsonResponse({'success': False, 'errors': pendencias})

    diario.diario_fechado = True
    diario.data_fechamento = timezone.now()
    diario.usuario_fechamento = request.user
    diario.save()
    messages.success(request, f'Diário de {disciplina.nome} - {turma.nome} fechado com sucesso!')
    return JsonResponse({'success': True, 'message': 'Diário fechado com sucesso!'})


@login_required
@require_POST
def abrir_diario(request, turma_id, disciplina_id):
    """Reabre o diário da disciplina"""
    turma, disciplina, _ = carregar_contexto(request, turma_id, disciplina_id)
    diario = obter_diario(turma, disciplina, request.user)
    diario.diario_fechado = False
    diario.data_reabertura = timezone.now()
    diario.usuario_reabertura = request.user
    diario.save()
    messages.success(request, f'Diário de {disciplina.nome} - {turma.nome} reaberto com sucesso!')
    return JsonResponse({'success': True, 'message': 'Diário reaberto com sucesso!'})
