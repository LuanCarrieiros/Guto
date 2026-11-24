"""
Cálculos dos relatórios de turma (boletim, frequência e desempenho).

As médias são normalizadas para a escala 0–10 e ponderadas pelo peso de cada avaliação.
A média e a frequência mínimas para aprovação podem ser ajustadas em
Utilitários > Configurações (chaves "media_aprovacao" e "frequencia_minima").
"""
from decimal import Decimal

from django.db.models import Q

from .models import Avaliacao, Disciplina, DivisaoPeriodoLetivo, NotaAvaliacao, RegistroFrequencia

MEDIA_APROVACAO_PADRAO = 6.0
MEDIA_RECUPERACAO = 4.0
FREQUENCIA_MINIMA_PADRAO = 75.0


def _config_numerica(chave, padrao):
    from utilitarios.models import ConfiguracaoSistema
    valor = ConfiguracaoSistema.objects.filter(chave=chave).values_list('valor', flat=True).first()
    try:
        return float(str(valor).replace(',', '.')) if valor is not None else padrao
    except ValueError:
        return padrao


def criterios_aprovacao():
    return {
        'media': _config_numerica('media_aprovacao', MEDIA_APROVACAO_PADRAO),
        'frequencia': _config_numerica('frequencia_minima', FREQUENCIA_MINIMA_PADRAO),
    }


def divisoes_da_turma(turma):
    return list(DivisaoPeriodoLetivo.objects.filter(
        periodo_letivo=turma.periodo_letivo, ativo=True
    ).order_by('ordem'))


def disciplinas_da_turma(turma):
    """Disciplinas com avaliações ou aulas registradas na turma."""
    return list(Disciplina.objects.filter(
        Q(avaliacao__turma=turma) | Q(aularegistrada__turma=turma)
    ).distinct().order_by('nome'))


def media_ponderada(notas):
    """Média (0–10) ponderada pelo peso; ausências valem zero e dispensas são ignoradas."""
    soma, pesos = Decimal('0'), Decimal('0')
    for nota in notas:
        avaliacao = nota.avaliacao
        if nota.dispensado or not avaliacao.valor_maximo:
            continue
        valor = Decimal('0') if nota.ausente or nota.nota is None else nota.nota
        soma += valor / avaliacao.valor_maximo * Decimal('10') * avaliacao.peso
        pesos += avaliacao.peso
    return float(soma / pesos) if pesos else None


def frequencia(registros):
    """Percentual de presença (faltas justificadas não contam como falta)."""
    total = len(registros)
    if not total:
        return None
    faltas = sum(1 for r in registros if r.situacao == 'AUSENTE')
    return (total - faltas) * 100 / total


def situacao(media, freq, criterios):
    if media is None:
        return 'CURSANDO'
    if freq is not None and freq < criterios['frequencia']:
        return 'REPROVADO'
    if media >= criterios['media']:
        return 'APROVADO'
    if media >= MEDIA_RECUPERACAO:
        return 'RECUPERACAO'
    return 'REPROVADO'


def calcular_boletim(turma, aluno):
    criterios = criterios_aprovacao()
    divisoes = divisoes_da_turma(turma)
    notas = list(NotaAvaliacao.objects.filter(
        aluno=aluno, avaliacao__turma=turma, avaliacao__ativo=True
    ).select_related('avaliacao'))
    presencas = list(RegistroFrequencia.objects.filter(aluno=aluno, aula__turma=turma).select_related('aula'))

    linhas = []
    for disciplina in disciplinas_da_turma(turma):
        notas_disc = [n for n in notas if n.avaliacao.disciplina_id == disciplina.pk]
        por_divisao = []
        for divisao in divisoes:
            por_divisao.append(media_ponderada([n for n in notas_disc if n.avaliacao.divisao_periodo_id == divisao.pk]))
        medias_validas = [m for m in por_divisao if m is not None]
        media = sum(medias_validas) / len(medias_validas) if medias_validas else None
        freq = frequencia([p for p in presencas if p.aula.disciplina_id == disciplina.pk])
        linhas.append({
            'disciplina': disciplina,
            'notas': por_divisao,
            'media': media,
            'frequencia': freq,
            'faltas': sum(1 for p in presencas if p.aula.disciplina_id == disciplina.pk and p.situacao == 'AUSENTE'),
            'situacao': situacao(media, freq, criterios),
        })

    medias = [l['media'] for l in linhas if l['media'] is not None]
    freqs = [l['frequencia'] for l in linhas if l['frequencia'] is not None]
    situacoes = [l['situacao'] for l in linhas]
    if not linhas or all(s == 'CURSANDO' for s in situacoes):
        final = 'CURSANDO'
    elif 'REPROVADO' in situacoes:
        final = 'REPROVADO'
    elif 'RECUPERACAO' in situacoes:
        final = 'RECUPERACAO'
    elif 'CURSANDO' in situacoes:
        final = 'CURSANDO'
    else:
        final = 'APROVADO'

    resumo = {
        'media_geral': sum(medias) / len(medias) if medias else None,
        'frequencia_geral': sum(freqs) / len(freqs) if freqs else None,
        'aprovadas': situacoes.count('APROVADO'),
        'recuperacao': situacoes.count('RECUPERACAO'),
        'reprovadas': situacoes.count('REPROVADO'),
        'situacao_final': final,
    }
    return {'divisoes': divisoes, 'linhas': linhas, 'resumo': resumo, 'criterios': criterios}


def calcular_frequencia_turma(turma, alunos):
    disciplinas = disciplinas_da_turma(turma)
    registros = list(RegistroFrequencia.objects.filter(aula__turma=turma).select_related('aula'))
    criterios = criterios_aprovacao()
    linhas = []
    for aluno in alunos:
        do_aluno = [r for r in registros if r.aluno_id == aluno.pk]
        celulas = [frequencia([r for r in do_aluno if r.aula.disciplina_id == d.pk]) for d in disciplinas]
        geral = frequencia(do_aluno)
        linhas.append({
            'aluno': aluno,
            'celulas': celulas,
            'geral': geral,
            'faltas': sum(1 for r in do_aluno if r.situacao == 'AUSENTE'),
            'abaixo': geral is not None and geral < criterios['frequencia'],
        })
    aulas_por_disciplina = [
        len({r.aula_id for r in registros if r.aula.disciplina_id == d.pk}) for d in disciplinas
    ]
    return {'disciplinas': disciplinas, 'linhas': linhas, 'aulas_por_disciplina': aulas_por_disciplina,
            'criterios': criterios}


def calcular_desempenho_turma(turma, alunos):
    criterios = criterios_aprovacao()
    notas = list(NotaAvaliacao.objects.filter(avaliacao__turma=turma, avaliacao__ativo=True).select_related('avaliacao'))
    disciplinas = []
    for disciplina in disciplinas_da_turma(turma):
        medias = []
        for aluno in alunos:
            m = media_ponderada([n for n in notas if n.aluno_id == aluno.pk and n.avaliacao.disciplina_id == disciplina.pk])
            if m is not None:
                medias.append(m)
        disciplinas.append({
            'disciplina': disciplina,
            'avaliacoes': Avaliacao.objects.filter(turma=turma, disciplina=disciplina, ativo=True).count(),
            'media': sum(medias) / len(medias) if medias else None,
            'maior': max(medias) if medias else None,
            'menor': min(medias) if medias else None,
            'abaixo': sum(1 for m in medias if m < criterios['media']),
            'avaliados': len(medias),
        })

    faixas = {'excelente': 0, 'bom': 0, 'regular': 0, 'insuficiente': 0}
    ranking = []
    for aluno in alunos:
        m = media_ponderada([n for n in notas if n.aluno_id == aluno.pk])
        if m is None:
            continue
        ranking.append({'aluno': aluno, 'media': m})
        if m >= 9:
            faixas['excelente'] += 1
        elif m >= 7:
            faixas['bom'] += 1
        elif m >= criterios['media']:
            faixas['regular'] += 1
        else:
            faixas['insuficiente'] += 1
    ranking.sort(key=lambda r: r['media'], reverse=True)
    total = len(ranking)
    faixas_pct = {k: (v * 100 / total if total else 0) for k, v in faixas.items()}
    medias = [r['media'] for r in ranking]
    return {
        'disciplinas': disciplinas,
        'ranking': ranking,
        'faixas': faixas,
        'faixas_pct': faixas_pct,
        'media_geral': sum(medias) / len(medias) if medias else None,
        'total_avaliados': total,
        'criterios': criterios,
    }
