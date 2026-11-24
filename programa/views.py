from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from dashboard.models import AtividadeRecente
from .forms import AulaProgramaForm, ModuloProgramaForm, ParticipanteProgramaForm, ProgramaPedagogicoForm
from .models import AulaPrograma, FrequenciaPrograma, ModuloPrograma, ParticipantePrograma, ProgramaPedagogico


def registrar(request, acao, objeto, descricao):
    AtividadeRecente.registrar_atividade(
        usuario=request.user, acao=acao, modulo='PROGRAMA',
        objeto_nome=str(objeto), objeto_id=objeto.pk, descricao=descricao,
    )


def form_page(request, form, title, cancel_url, icon='fa-book-open', subtitle=None, submit_label=None):
    return render(request, 'generic/form.html', {
        'form': form, 'title': title, 'subtitle': subtitle, 'icon': icon,
        'cancel_url': cancel_url, 'submit_label': submit_label,
    })


@login_required
def programa_home(request):
    """
    Página inicial do módulo Programa Pedagógico
    """
    hoje = date.today()
    context = {
        'total_programas': ProgramaPedagogico.objects.count(),
        'programas_ativos': ProgramaPedagogico.objects.filter(status='ATIVO').count(),
        'total_participantes': ParticipantePrograma.objects.filter(ativo=True).count(),
        'aulas_proximas': AulaPrograma.objects.filter(
            data_planejada__gte=hoje, status='PLANEJADA'
        ).select_related('modulo', 'modulo__programa').order_by('data_planejada', 'horario_inicio')[:6],
        'programas_recentes': ProgramaPedagogico.objects.annotate(
            ativos=Count('participantes', filter=Q(participantes__ativo=True))
        ).order_by('-data_cadastro')[:5],
    }
    return render(request, 'programa/programa_home.html', context)


# ============================== PROGRAMAS ==============================

@login_required
def programa_list(request):
    """
    Lista de programas pedagógicos
    """
    programas = ProgramaPedagogico.objects.select_related('coordenador').annotate(
        ativos=Count('participantes', filter=Q(participantes__ativo=True), distinct=True),
        total_modulos=Count('modulos', distinct=True),
    ).order_by('-data_inicio', 'nome')
    busca = request.GET.get('busca', '').strip()
    status = request.GET.get('status', '')
    tipo = request.GET.get('tipo', '')
    if busca:
        programas = programas.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))
    if status:
        programas = programas.filter(status=status)
    if tipo:
        programas = programas.filter(tipo_programa=tipo)

    context = {
        'page_obj': Paginator(programas, 15).get_page(request.GET.get('page')),
        'busca': busca,
        'status': status,
        'tipo': tipo,
        'status_choices': ProgramaPedagogico.STATUS_CHOICES,
        'tipo_choices': ProgramaPedagogico.TIPO_PROGRAMA_CHOICES,
    }
    return render(request, 'programa/programa_list.html', context)


@login_required
def programa_create(request):
    """
    Criar novo programa pedagógico
    """
    form = ProgramaPedagogicoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        programa = form.save(commit=False)
        programa.usuario_cadastro = request.user
        programa.save()
        registrar(request, 'CRIAR', programa, 'Novo programa pedagógico')
        messages.success(request, f'Programa "{programa.nome}" criado. Cadastre agora os módulos.')
        return redirect('programa:programa_detail', pk=programa.pk)
    return form_page(request, form, 'Novo Programa Pedagógico', reverse('programa:programa_list'),
                     submit_label='Criar programa')


@login_required
def programa_detail(request, pk):
    """
    Detalhes do programa pedagógico
    """
    programa = get_object_or_404(ProgramaPedagogico.objects.select_related('coordenador', 'usuario_cadastro'), pk=pk)
    modulos = programa.modulos.select_related('professor_responsavel').annotate(total_aulas=Count('aulas'))
    context = {
        'programa': programa,
        'modulos': modulos,
        'participantes': programa.participantes.filter(ativo=True).select_related('aluno').order_by('aluno__nome')[:10],
        'total_participantes': programa.total_participantes,
        'total_aulas': AulaPrograma.objects.filter(modulo__programa=programa).count(),
        'aulas_realizadas': AulaPrograma.objects.filter(modulo__programa=programa, status='REALIZADA').count(),
    }
    return render(request, 'programa/programa_detail.html', context)


@login_required
def programa_edit(request, pk):
    """
    Editar programa pedagógico
    """
    programa = get_object_or_404(ProgramaPedagogico, pk=pk)
    form = ProgramaPedagogicoForm(request.POST or None, instance=programa)
    if request.method == 'POST' and form.is_valid():
        form.save()
        registrar(request, 'EDITAR', programa, 'Programa pedagógico atualizado')
        messages.success(request, 'Programa atualizado com sucesso!')
        return redirect('programa:programa_detail', pk=programa.pk)
    return form_page(request, form, 'Editar Programa Pedagógico', reverse('programa:programa_detail', args=[pk]),
                     subtitle=programa.nome)


# ============================== MÓDULOS ==============================

@login_required
def modulo_list(request):
    """
    Lista de módulos de todos os programas
    """
    modulos = ModuloPrograma.objects.select_related('programa', 'professor_responsavel').annotate(
        total_aulas=Count('aulas')
    ).order_by('programa__nome', 'ordem')
    programa_id = request.GET.get('programa', '')
    if programa_id:
        modulos = modulos.filter(programa_id=programa_id)
    context = {
        'modulos': modulos,
        'programas': ProgramaPedagogico.objects.order_by('nome'),
        'programa_id': programa_id,
    }
    return render(request, 'programa/modulo_list.html', context)


@login_required
def modulo_create(request):
    """
    Criar novo módulo (o programa pode vir pré-selecionado por ?programa=)
    """
    programa = ProgramaPedagogico.objects.filter(pk=request.GET.get('programa')).first()
    inicial = {}
    if programa:
        inicial = {
            'programa': programa.pk,
            'ordem': programa.modulos.count() + 1,
            'data_inicio': programa.data_inicio,
            'data_fim': programa.data_fim,
        }
    form = ModuloProgramaForm(request.POST or None, initial=inicial)
    if request.method == 'POST' and form.is_valid():
        modulo = form.save()
        messages.success(request, f'Módulo "{modulo.nome}" criado com sucesso!')
        return redirect('programa:modulo_detail', pk=modulo.pk)
    cancelar = reverse('programa:programa_detail', args=[programa.pk]) if programa else reverse('programa:modulo_list')
    return form_page(request, form, 'Novo Módulo', cancelar, icon='fa-layer-group', submit_label='Criar módulo')


@login_required
def modulo_detail(request, pk):
    """
    Detalhes do módulo
    """
    modulo = get_object_or_404(ModuloPrograma.objects.select_related('programa', 'professor_responsavel'), pk=pk)
    context = {
        'modulo': modulo,
        'aulas': modulo.aulas.select_related('professor').order_by('numero_aula'),
    }
    return render(request, 'programa/modulo_detail.html', context)


@login_required
def modulo_edit(request, pk):
    """
    Editar módulo
    """
    modulo = get_object_or_404(ModuloPrograma, pk=pk)
    form = ModuloProgramaForm(request.POST or None, instance=modulo)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Módulo atualizado com sucesso!')
        return redirect('programa:modulo_detail', pk=modulo.pk)
    return form_page(request, form, 'Editar Módulo', reverse('programa:modulo_detail', args=[pk]),
                     icon='fa-layer-group', subtitle=str(modulo))


# ============================== PARTICIPANTES ==============================

@login_required
def participante_list(request, programa_pk):
    """
    Lista de participantes do programa, com atualização de situação
    """
    programa = get_object_or_404(ProgramaPedagogico, pk=programa_pk)

    if request.method == 'POST':
        participante = get_object_or_404(ParticipantePrograma, pk=request.POST.get('participante'), programa=programa)
        situacao = request.POST.get('situacao')
        if situacao in dict(ParticipantePrograma.SITUACAO_CHOICES):
            participante.situacao = situacao
            participante.ativo = situacao in ('INSCRITO', 'ATIVO', 'SUSPENSO')
            if situacao in ('CONCLUIDO', 'REPROVADO') and not participante.data_conclusao:
                participante.data_conclusao = date.today()
            participante.save()
            messages.success(request, f'Situação de {participante.aluno.nome} atualizada.')
        return redirect('programa:participante_list', programa_pk=programa.pk)

    context = {
        'programa': programa,
        'participantes': programa.participantes.select_related('aluno').order_by('-ativo', 'aluno__nome'),
        'situacoes': ParticipantePrograma.SITUACAO_CHOICES,
    }
    return render(request, 'programa/participante_list.html', context)


@login_required
def participante_create(request, programa_pk):
    """
    Inscrever participante no programa
    """
    programa = get_object_or_404(ProgramaPedagogico, pk=programa_pk)
    lista_url = reverse('programa:participante_list', args=[programa.pk])
    if programa.vagas_restantes <= 0:
        messages.error(request, 'Não há vagas disponíveis neste programa.')
        return redirect(lista_url)

    form = ParticipanteProgramaForm(request.POST or None, programa=programa,
                                    initial={'data_inscricao': date.today(), 'situacao': 'INSCRITO'})
    if request.method == 'POST' and form.is_valid():
        participante = form.save(commit=False)
        participante.programa = programa
        participante.usuario_cadastro = request.user
        participante.save()
        messages.success(request, f'{participante.aluno.nome} inscrito(a) no programa.')
        return redirect(lista_url)
    return form_page(request, form, 'Inscrever Participante', lista_url, icon='fa-user-plus',
                     subtitle=f'{programa.nome} · {programa.vagas_restantes} vaga(s)', submit_label='Inscrever')


# ============================== AULAS ==============================

@login_required
def aula_list(request):
    """
    Lista de aulas
    """
    aulas = AulaPrograma.objects.select_related('modulo', 'modulo__programa', 'professor').order_by(
        '-data_planejada', 'horario_inicio')
    programa_id = request.GET.get('programa', '')
    status = request.GET.get('status', '')
    if programa_id:
        aulas = aulas.filter(modulo__programa_id=programa_id)
    if status:
        aulas = aulas.filter(status=status)
    context = {
        'page_obj': Paginator(aulas, 20).get_page(request.GET.get('page')),
        'programas': ProgramaPedagogico.objects.order_by('nome'),
        'programa_id': programa_id,
        'status': status,
        'status_choices': AulaPrograma.STATUS_CHOICES,
    }
    return render(request, 'programa/aula_list.html', context)


@login_required
def aula_create(request):
    """
    Criar nova aula (o módulo pode vir pré-selecionado por ?modulo=)
    """
    modulo = ModuloPrograma.objects.filter(pk=request.GET.get('modulo')).select_related('programa').first()
    inicial = {'data_planejada': date.today()}
    if modulo:
        inicial.update({
            'modulo': modulo.pk,
            'numero_aula': modulo.aulas.count() + 1,
            'professor': modulo.professor_responsavel_id,
        })
    form = AulaProgramaForm(request.POST or None, initial=inicial)
    if request.method == 'POST' and form.is_valid():
        aula = form.save(commit=False)
        aula.usuario_cadastro = request.user
        aula.save()
        messages.success(request, f'Aula "{aula.titulo}" cadastrada com sucesso!')
        return redirect('programa:modulo_detail', pk=aula.modulo_id)
    cancelar = reverse('programa:modulo_detail', args=[modulo.pk]) if modulo else reverse('programa:aula_list')
    return form_page(request, form, 'Nova Aula', cancelar, icon='fa-chalkboard', submit_label='Cadastrar aula')


@login_required
def frequencia_aula(request, pk):
    """
    Registrar frequência da aula e recalcular a frequência total dos participantes
    """
    aula = get_object_or_404(AulaPrograma.objects.select_related('modulo', 'modulo__programa'), pk=pk)
    programa = aula.modulo.programa
    participantes = programa.participantes.filter(ativo=True).select_related('aluno').order_by('aluno__nome')
    registros = {f.participante_id: f for f in aula.frequencias.all()}

    if request.method == 'POST':
        presentes = set(request.POST.getlist('presentes'))
        with transaction.atomic():
            for participante in participantes:
                presente = str(participante.pk) in presentes
                justificativa = request.POST.get(f'justificativa_{participante.pk}', '').strip() or None
                FrequenciaPrograma.objects.update_or_create(
                    participante=participante, aula=aula,
                    defaults={
                        'presente': presente,
                        'justificativa_falta': None if presente else justificativa,
                        'usuario_cadastro': request.user,
                    },
                )
            aula.presentes = aula.frequencias.filter(presente=True).count()
            aula.ausentes = aula.frequencias.filter(presente=False).count()
            if aula.status == 'PLANEJADA':
                aula.status = 'REALIZADA'
                aula.data_realizada = aula.data_realizada or date.today()
            aula.save()

            # Frequência total (%) de cada participante no programa
            for participante in participantes:
                total = participante.frequencias.count()
                presencas = participante.frequencias.filter(presente=True).count()
                participante.frequencia_total = round(presencas * 100 / total, 2) if total else 0
                participante.save(update_fields=['frequencia_total'])
        messages.success(request, f'Frequência registrada: {aula.presentes} presente(s), {aula.ausentes} ausente(s).')
        return redirect('programa:modulo_detail', pk=aula.modulo_id)

    linhas = [
        {
            'participante': p,
            'presente': registros[p.pk].presente if p.pk in registros else True,
            'justificativa': registros[p.pk].justificativa_falta if p.pk in registros else '',
        }
        for p in participantes
    ]
    context = {
        'aula': aula,
        'programa': programa,
        'linhas': linhas,
        'ja_registrada': bool(registros),
    }
    return render(request, 'programa/frequencia_aula.html', context)
