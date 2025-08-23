from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.core.paginator import Paginator
from datetime import date, datetime
from .models import TipoRelatorio, FiltroRelatorio, CalendarioEscolar, EventoCalendario
from .forms import FiltroRelatorioForm, CalendarioEscolarForm, EventoCalendarioForm
import calendar

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
            
            # Gerar relatório (simulação)
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

@login_required
def gerar_relatorio(request, filtro_id):
    """
    Gerar e exibir relatório com base nos filtros aplicados
    """
    filtro = get_object_or_404(FiltroRelatorio, pk=filtro_id, usuario=request.user)
    
    # Dados simulados para o relatório
    dados_relatorio = {
        'filtro': filtro,
        'total_turmas': 15,
        'total_alunos': 350,
        'data_geracao': datetime.now(),
        'turmas_encontradas': [
            {'nome': '1º A - Matutino', 'alunos': 25, 'status': 'Ativo'},
            {'nome': '2º B - Vespertino', 'alunos': 28, 'status': 'Ativo'},
            {'nome': '3º C - Matutino', 'alunos': 22, 'status': 'Ativo'},
        ]
    }
    
    if request.GET.get('format') == 'print':
        return render(request, 'opcoes/documentos/relatorio_print.html', dados_relatorio)
    
    context = {
        **dados_relatorio,
        'title': f'Relatório - {filtro.tipo_relatorio}'
    }
    return render(request, 'opcoes/documentos/relatorio_resultado.html', context)

# === MÓDULO CALENDÁRIO ESCOLAR (RF701-RF704) ===

@login_required
def calendario_escolar(request):
    """
    Exibir calendário escolar do ano administrativo (RF701-RF702)
    """
    ano_atual = date.today().year
    ano = request.GET.get('ano', ano_atual)
    
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = ano_atual
    
    # Buscar calendários do ano
    calendarios = CalendarioEscolar.objects.filter(
        periodo_letivo=str(ano),
        ativo=True
    ).select_related('usuario_criacao')
    
    # Criar calendário HTML
    cal = calendar.HTMLCalendar(calendar.MONDAY)
    
    # Buscar eventos do ano
    eventos = EventoCalendario.objects.filter(
        calendario__periodo_letivo=str(ano),
        data_evento__year=ano
    ).select_related('calendario')
    
    eventos_por_data = {}
    for evento in eventos:
        data_str = evento.data_evento.strftime('%Y-%m-%d')
        if data_str not in eventos_por_data:
            eventos_por_data[data_str] = []
        eventos_por_data[data_str].append(evento)
    
    meses_html = []
    for mes in range(1, 13):
        mes_html = cal.formatmonth(ano, mes)
        meses_html.append({
            'mes': calendar.month_name[mes],
            'numero': mes,
            'html': mes_html
        })
    
    context = {
        'ano': ano,
        'calendarios': calendarios,
        'eventos_por_data': eventos_por_data,
        'meses': meses_html,
        'anos_disponiveis': range(ano-5, ano+6),
        'title': f'Calendário Escolar {ano}'
    }
    
    # Se for requisição para impressão
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
        'action': 'Criar'
    }
    return render(request, 'opcoes/calendario/calendario_form.html', context)

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
            return redirect('opcoes:calendario_escolar')
    else:
        form = CalendarioEscolarForm(instance=calendario)
    
    context = {
        'form': form,
        'calendario': calendario,
        'title': f'Editar Calendário Escolar - {calendario}',
        'action': 'Editar'
    }
    return render(request, 'opcoes/calendario/calendario_form.html', context)

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
        'title': f'Criar Evento - {calendario}',
        'action': 'Criar'
    }
    return render(request, 'opcoes/calendario/evento_form.html', context)
