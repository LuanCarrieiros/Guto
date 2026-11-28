import calendar
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from turma.models import Turma
from .models import TipoRelatorio, FiltroRelatorio, CalendarioEscolar, EventoCalendario
from .forms import FiltroRelatorioForm, CalendarioEscolarForm, EventoCalendarioForm

@login_required
def opcoes_home(request):
    """
    View principal do módulo Opções (RF601)
    """
    return render(request, 'opcoes/opcoes_home.html')

# === MÓDULO DOCUMENTOS (RF603-RF607) ===

@login_required
def documentos_home(request):
    """
    Tela inicial de documentos - Emitir Relatórios de Alunos (RF603-RF604)
    """
    # Criar os tipos de relatórios se não existirem
    tipos_relatorio = []
    for tipo, nome in TipoRelatorio.TIPOS_RELATORIO:
        relatorio, created = TipoRelatorio.objects.get_or_create(
            nome=tipo,
            defaults={'descricao': f'Relatório de {nome}', 'ativo': True}
        )
        tipos_relatorio.append(relatorio)
    
    context = {
        'tipos_relatorio': tipos_relatorio,
        'title': 'Emitir Relatórios de Alunos'
    }
    return render(request, 'opcoes/documentos/documentos_home.html', context)

@login_required
def selecionar_relatorio(request, tipo_relatorio_id):
    """
    Selecionar tipo de relatório e mostrar tela de filtros (RF606-RF607)
    """
    tipo_relatorio = get_object_or_404(TipoRelatorio, pk=tipo_relatorio_id)
    
    if request.method == 'POST':
        form = FiltroRelatorioForm(request.POST)
        if form.is_valid():
            filtro = form.save(commit=False)
            filtro.tipo_relatorio = tipo_relatorio
            filtro.usuario = request.user
            filtro.save()
            
            messages.success(request, f'Relatório "{tipo_relatorio}" gerado com sucesso!')
            return redirect('opcoes:gerar_relatorio', filtro_id=filtro.id)
    else:
        form = FiltroRelatorioForm(initial={
            'periodo_letivo': str(date.today().year),
            'tipo_ensino': 'TODOS',
            'turno': 'TODOS',
            'status_diario': 'TODOS',
            'situacao_turma': 'TODOS'
        })
    
    context = {
        'tipo_relatorio': tipo_relatorio,
        'form': form,
        'title': f'Pesquisar Turmas - {tipo_relatorio}'
    }
    return render(request, 'opcoes/documentos/filtro_relatorio.html', context)

# Correspondência entre os tipos de ensino do filtro e os da Turma
TIPO_ENSINO_TURMA = {
    'INFANTIL': 'EDUCACAO_INFANTIL',
    'FUNDAMENTAL_I': 'ENSINO_FUNDAMENTAL_I',
    'FUNDAMENTAL_II': 'ENSINO_FUNDAMENTAL_II',
    'MEDIO': 'ENSINO_MEDIO',
}


def buscar_turmas_relatorio(filtro):
    """Aplica os filtros do relatório (RF607) sobre as turmas cadastradas."""
    turmas = Turma.objects.filter(periodo_letivo=filtro.periodo_letivo).annotate(
        total_alunos=Count('enturmacoes', filter=Q(enturmacoes__ativo=True))
    ).order_by('nome')

    if filtro.tipo_ensino != 'TODOS':
        turmas = turmas.filter(tipo_ensino=TIPO_ENSINO_TURMA.get(filtro.tipo_ensino, filtro.tipo_ensino))
    if filtro.turno != 'TODOS':
        turmas = turmas.filter(turno=filtro.turno)
    if filtro.status_diario == 'ABERTO':
        turmas = turmas.filter(diario_fechado=False)
    elif filtro.status_diario == 'FECHADO':
        turmas = turmas.filter(diario_fechado=True)
    # Turmas de anos anteriores ao corrente são consideradas encerradas
    ano_corrente = str(date.today().year)
    if filtro.situacao_turma == 'ATIVO':
        turmas = turmas.filter(periodo_letivo__gte=ano_corrente)
    elif filtro.situacao_turma == 'ENCERRADO':
        turmas = turmas.filter(periodo_letivo__lt=ano_corrente)

    turmas = list(turmas)
    if filtro.ano_serie:
        termo = filtro.ano_serie.strip().lower()
        turmas = [
            t for t in turmas
            if termo in t.ano_serie.lower() or termo in t.get_ano_serie_display().lower()
        ]
    return turmas


@login_required
def gerar_relatorio(request, filtro_id):
    """
    Gerar e exibir relatório com base nos filtros aplicados
    """
    filtro = get_object_or_404(FiltroRelatorio, pk=filtro_id, usuario=request.user)
    turmas = buscar_turmas_relatorio(filtro)

    turmas_encontradas = []
    for turma in turmas:
        enturmacoes = turma.enturmacoes.filter(ativo=True).select_related('aluno').order_by('aluno__nome')
        turmas_encontradas.append({
            'turma': turma,
            'alunos': [e.aluno for e in enturmacoes],
        })

    dados_relatorio = {
        'filtro': filtro,
        'tipo_relatorio': filtro.tipo_relatorio,
        'total_turmas': len(turmas),
        'total_alunos': sum(t.total_alunos for t in turmas),
        'data_geracao': timezone.now(),
        'turmas_encontradas': turmas_encontradas,
        'title': f'Relatório - {filtro.tipo_relatorio}',
    }

    if request.GET.get('format') == 'print':
        return render(request, 'opcoes/documentos/relatorio_print.html', dados_relatorio)

    return render(request, 'opcoes/documentos/relatorio_resultado.html', dados_relatorio)

# === MÓDULO CALENDÁRIO ESCOLAR (RF701-RF704) ===

MESES_PT = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]

# Cor (classes Tailwind) de cada tipo de evento no calendário visual
CORES_EVENTO = {
    'AULA': 'bg-green-100 text-green-800',
    'FERIADO': 'bg-red-100 text-red-800',
    'RECESSO': 'bg-orange-100 text-orange-800',
    'EVENTO_ESPECIAL': 'bg-yellow-100 text-yellow-800',
    'REUNIAO_PEDAGOGICA': 'bg-blue-100 text-blue-800',
    'FORMACAO': 'bg-purple-100 text-purple-800',
}


def montar_meses(ano, eventos):
    """Monta a estrutura (semanas/dias) dos 12 meses com os eventos de cada dia."""
    eventos_por_data = {}
    for evento in eventos:
        eventos_por_data.setdefault(evento.data_evento, []).append(evento)

    hoje = date.today()
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    meses = []
    for mes in range(1, 13):
        semanas = []
        for semana in cal.monthdatescalendar(ano, mes):
            dias = []
            for dia in semana:
                eventos_dia = eventos_por_data.get(dia, []) if dia.month == mes else []
                dias.append({
                    'data': dia,
                    'no_mes': dia.month == mes,
                    'hoje': dia == hoje,
                    'fim_de_semana': dia.weekday() >= 5,
                    'eventos': eventos_dia,
                    'cor': CORES_EVENTO.get(eventos_dia[0].tipo_evento, '') if eventos_dia else '',
                })
            semanas.append(dias)
        meses.append({
            'numero': mes,
            'nome': MESES_PT[mes - 1],
            'semanas': semanas,
            'eventos': [e for e in eventos if e.data_evento.month == mes],
        })
    return meses


@login_required
def calendario_escolar(request):
    """
    Exibir calendário escolar do ano administrativo (RF701-RF702)
    """
    ano_atual = date.today().year
    try:
        ano = int(request.GET.get('ano', ano_atual))
    except (ValueError, TypeError):
        ano = ano_atual

    calendarios = CalendarioEscolar.objects.filter(
        periodo_letivo=str(ano),
        ativo=True
    ).select_related('usuario_criacao')

    eventos = list(EventoCalendario.objects.filter(
        calendario__periodo_letivo=str(ano),
        calendario__ativo=True,
        data_evento__year=ano
    ).select_related('calendario').order_by('data_evento'))

    context = {
        'ano': ano,
        'calendarios': calendarios,
        'meses': montar_meses(ano, eventos),
        'total_eventos': len(eventos),
        'tipos_evento': [
            (codigo, nome, CORES_EVENTO[codigo])
            for codigo, nome in EventoCalendario.TIPO_EVENTO_CHOICES
        ],
        'anos_disponiveis': range(ano - 5, ano + 6),
        'title': f'Calendário Escolar {ano}'
    }

    if request.GET.get('format') == 'print':
        return render(request, 'opcoes/calendario/calendario_print.html', context)

    return render(request, 'opcoes/calendario/calendario_escolar.html', context)

@login_required
def calendario_criar(request):
    """
    Criar novo calendário escolar
    """
    if request.method == 'POST':
        form = CalendarioEscolarForm(request.POST)
        if form.is_valid():
            calendario = form.save(commit=False)
            calendario.usuario_criacao = request.user
            calendario.save()
            messages.success(request, 'Calendário escolar criado com sucesso!')
            return redirect('opcoes:calendario_escolar')
    else:
        form = CalendarioEscolarForm(initial={
            'periodo_letivo': str(date.today().year),
            'data_inicio_letivo': date(date.today().year, 2, 1),
            'data_fim_letivo': date(date.today().year, 12, 15),
        })
    
    context = {
        'form': form,
        'title': 'Criar Calendário Escolar',
        'subtitle': 'Configure o período letivo por tipo de ensino, série e turno',
        'icon': 'fa-calendar-plus',
        'cancel_url': reverse('opcoes:calendario_escolar'),
        'submit_label': 'Criar calendário',
    }
    return render(request, 'generic/form.html', context)

@login_required
def calendario_editar(request, pk):
    """
    Editar calendário escolar existente
    """
    calendario = get_object_or_404(CalendarioEscolar, pk=pk)
    
    if request.method == 'POST':
        form = CalendarioEscolarForm(request.POST, instance=calendario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Calendário escolar atualizado com sucesso!')
            return redirect('opcoes:calendario_detalhe', pk=calendario.pk)
    else:
        form = CalendarioEscolarForm(instance=calendario)
    
    context = {
        'form': form,
        'calendario': calendario,
        'title': 'Editar Calendário Escolar',
        'subtitle': str(calendario),
        'icon': 'fa-calendar-alt',
        'cancel_url': reverse('opcoes:calendario_detalhe', args=[calendario.pk]),
    }
    return render(request, 'generic/form.html', context)

@login_required
def calendario_detalhe(request, pk):
    """
    Visualizar detalhes do calendário escolar
    """
    calendario = get_object_or_404(CalendarioEscolar, pk=pk)
    eventos = calendario.eventos.all().order_by('data_evento')
    
    context = {
        'calendario': calendario,
        'eventos': eventos,
        'title': f'Calendário - {calendario}'
    }
    return render(request, 'opcoes/calendario/calendario_detail.html', context)

@login_required
def evento_criar(request, calendario_id):
    """
    Criar evento no calendário
    """
    calendario = get_object_or_404(CalendarioEscolar, pk=calendario_id)
    
    if request.method == 'POST':
        form = EventoCalendarioForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.calendario = calendario
            evento.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('opcoes:calendario_detalhe', pk=calendario.pk)
    else:
        form = EventoCalendarioForm()
    
    context = {
        'form': form,
        'calendario': calendario,
        'title': 'Novo Evento',
        'subtitle': f'Calendário {calendario}',
        'icon': 'fa-calendar-day',
        'cancel_url': reverse('opcoes:calendario_detalhe', args=[calendario.pk]),
        'submit_label': 'Cadastrar evento',
    }
    return render(request, 'generic/form.html', context)
