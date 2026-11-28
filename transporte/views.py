from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from dashboard.models import AtividadeRecente
from .forms import (
    AlunoTransporteForm, ManutencaoVeiculoForm, MotoristaForm, PontoParadaForm, RegistroViagemForm,
    RotaForm, VeiculoForm,
)
from .models import (
    AlunoTransporte, ManutencaoVeiculo, Motorista, PontoParada, RegistroViagem, Rota, Veiculo,
)

MESES_PT = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto',
            'Setembro', 'Outubro', 'Novembro', 'Dezembro']


def registrar(request, acao, objeto, descricao):
    AtividadeRecente.registrar_atividade(
        usuario=request.user, acao=acao, modulo='TRANSPORTE',
        objeto_nome=str(objeto), objeto_id=objeto.pk, descricao=descricao,
    )


def km_percorridos(viagens):
    """Soma dos km de cada viagem (km_final - km_inicial)."""
    return viagens.filter(km_final__isnull=False, km_inicial__isnull=False).aggregate(
        total=Sum(F('km_final') - F('km_inicial'))
    )['total'] or 0


def form_page(request, form, title, cancel_url, icon='fa-bus', subtitle=None, submit_label=None):
    return render(request, 'generic/form.html', {
        'form': form, 'title': title, 'subtitle': subtitle, 'icon': icon,
        'cancel_url': cancel_url, 'submit_label': submit_label,
    })


@login_required
def transporte_home(request):
    """
    Dashboard principal do módulo Transporte Escolar
    """
    # Estatísticas gerais
    total_motoristas = Motorista.objects.filter(ativo=True).count()
    total_veiculos = Veiculo.objects.filter(status='ATIVO').count()
    total_rotas = Rota.objects.filter(ativa=True).count()
    total_alunos = AlunoTransporte.objects.filter(ativo=True).count()
    
    # Alertas importantes
    alertas = []
    
    # CNHs vencidas ou próximas do vencimento
    cnhs_vencendo = Motorista.objects.filter(
        ativo=True,
        cnh_validade__lte=date.today() + timedelta(days=30)
    ).count()
    if cnhs_vencendo > 0:
        alertas.append({
            'tipo': 'warning',
            'titulo': 'CNHs Vencendo',
            'mensagem': f'{cnhs_vencendo} motorista(s) com CNH vencida ou vencendo em 30 dias',
            'icone': 'fa-id-card',
            'link': reverse('transporte:motorista_list') + '?alerta=cnh'
        })
    
    # Veículos em manutenção
    veiculos_manutencao = Veiculo.objects.filter(status='MANUTENCAO').count()
    if veiculos_manutencao > 0:
        alertas.append({
            'tipo': 'info',
            'titulo': 'Veículos em Manutenção',
            'mensagem': f'{veiculos_manutencao} veículo(s) em manutenção',
            'icone': 'fa-wrench',
            'link': reverse('transporte:veiculo_list') + '?status=manutencao'
        })
    
    # Vistorias vencidas
    vistorias_vencidas = Veiculo.objects.filter(
        status='ATIVO',
        proxima_vistoria__lt=date.today()
    ).count()
    if vistorias_vencidas > 0:
        alertas.append({
            'tipo': 'error',
            'titulo': 'Vistorias Vencidas',
            'mensagem': f'{vistorias_vencidas} veículo(s) com vistoria vencida',
            'icone': 'fa-clipboard-check',
            'link': reverse('transporte:veiculo_list') + '?alerta=vistoria'
        })
    
    # Rotas mais utilizadas
    rotas_populares = Rota.objects.filter(ativa=True).annotate(
        alunos_ativos=Count('alunos_rota', filter=Q(alunos_rota__ativo=True))
    ).order_by('-alunos_ativos')[:5]
    
    # Viagens recentes
    viagens_recentes = RegistroViagem.objects.select_related(
        'rota', 'motorista', 'veiculo'
    ).order_by('-data_viagem', '-tipo_viagem')[:10]
    
    # Manutenções pendentes
    manutencoes_pendentes = ManutencaoVeiculo.objects.filter(
        status__in=['AGENDADA', 'EM_ANDAMENTO']
    ).select_related('veiculo').order_by('data_agendamento')[:5]
    
    context = {
        'title': 'Transporte Escolar - Dashboard',
        'total_motoristas': total_motoristas,
        'total_veiculos': total_veiculos,
        'total_rotas': total_rotas,
        'total_alunos': total_alunos,
        'alertas': alertas,
        'rotas_populares': rotas_populares,
        'viagens_recentes': viagens_recentes,
        'manutencoes_pendentes': manutencoes_pendentes,
        'cnhs_vencendo': cnhs_vencendo,
        'veiculos_manutencao': veiculos_manutencao,
        'vistorias_vencidas': vistorias_vencidas,
    }
    return render(request, 'transporte/transporte_home.html', context)

# ================ MOTORISTAS ================

@login_required
def motorista_list(request):
    """
    Lista de motoristas com filtros e busca
    """
    motoristas = Motorista.objects.all()
    
    # Filtros
    busca = request.GET.get('busca', '')
    ativo = request.GET.get('ativo', '')
    alerta = request.GET.get('alerta', '')
    
    if busca:
        motoristas = motoristas.filter(
            Q(nome__icontains=busca) | 
            Q(cpf__icontains=busca) |
            Q(cnh_numero__icontains=busca)
        )
    
    if ativo == 'sim':
        motoristas = motoristas.filter(ativo=True)
    elif ativo == 'nao':
        motoristas = motoristas.filter(ativo=False)
        
    if alerta == 'cnh':
        motoristas = motoristas.filter(
            cnh_validade__lte=date.today() + timedelta(days=30)
        )
    
    motoristas = motoristas.order_by('nome')
    
    # Paginação
    paginator = Paginator(motoristas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Motoristas',
        'page_obj': page_obj,
        'busca': busca,
        'ativo': ativo,
        'alerta': alerta,
    }
    return render(request, 'transporte/motorista_list.html', context)

@login_required
def motorista_create(request):
    """Criar novo motorista"""
    form = MotoristaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        motorista = form.save(commit=False)
        motorista.usuario_cadastro = request.user
        motorista.save()
        registrar(request, 'CRIAR', motorista, 'Novo motorista cadastrado')
        messages.success(request, f'Motorista "{motorista.nome}" criado com sucesso!')
        return redirect('transporte:motorista_detail', pk=motorista.pk)
    return form_page(request, form, 'Novo Motorista', reverse('transporte:motorista_list'),
                     icon='fa-id-card', submit_label='Cadastrar motorista')

@login_required
def motorista_detail(request, pk):
    """
    Detalhes do motorista
    """
    motorista = get_object_or_404(Motorista, pk=pk)
    
    # Rotas do motorista
    rotas_ativas = Rota.objects.filter(motorista=motorista, ativa=True)
    
    # Viagens recentes
    viagens_recentes = RegistroViagem.objects.filter(
        motorista=motorista
    ).select_related('rota', 'veiculo').order_by('-data_viagem')[:10]
    
    # Estatísticas
    total_viagens = RegistroViagem.objects.filter(motorista=motorista).count()
    km_total = km_percorridos(RegistroViagem.objects.filter(motorista=motorista))
    
    context = {
        'title': f'Motorista: {motorista.nome}',
        'motorista': motorista,
        'rotas_ativas': rotas_ativas,
        'viagens_recentes': viagens_recentes,
        'total_viagens': total_viagens,
        'km_percorridos': km_total,
    }
    return render(request, 'transporte/motorista_detail.html', context)

@login_required
def motorista_edit(request, pk):
    """Editar motorista"""
    motorista = get_object_or_404(Motorista, pk=pk)
    form = MotoristaForm(request.POST or None, instance=motorista)
    if request.method == 'POST' and form.is_valid():
        form.save()
        registrar(request, 'EDITAR', motorista, 'Motorista atualizado')
        messages.success(request, f'Motorista "{motorista.nome}" atualizado com sucesso!')
        return redirect('transporte:motorista_detail', pk=motorista.pk)
    return form_page(request, form, 'Editar Motorista', reverse('transporte:motorista_detail', args=[pk]),
                     icon='fa-id-card', subtitle=motorista.nome)

@login_required
def motorista_delete(request, pk):
    """Excluir motorista (somente sem rotas ativas)"""
    motorista = get_object_or_404(Motorista, pk=pk)
    if Rota.objects.filter(motorista=motorista, ativa=True).exists():
        messages.error(request, 'Não é possível excluir motorista com rotas ativas.')
        return redirect('transporte:motorista_detail', pk=pk)
    if motorista.registroviagem_set.exists():
        messages.error(request, 'Motorista possui viagens registradas. Desative-o em vez de excluir.')
        return redirect('transporte:motorista_detail', pk=pk)

    if request.method == 'POST' and request.POST.get('confirmar') == 'sim':
        nome_motorista = motorista.nome
        registrar(request, 'DELETAR', motorista, 'Motorista excluído')
        motorista.delete()
        messages.success(request, f'Motorista "{nome_motorista}" excluído com sucesso!')
        return redirect('transporte:motorista_list')

    return render(request, 'generic/confirm_delete.html', {
        'title': 'Excluir Motorista',
        'object_label': motorista.nome,
        'cancel_url': reverse('transporte:motorista_detail', args=[pk]),
    })

# ================ VEÍCULOS ================

@login_required
def veiculo_list(request):
    """
    Lista de veículos com filtros
    """
    veiculos = Veiculo.objects.all()
    
    # Filtros
    busca = request.GET.get('busca', '')
    status = request.GET.get('status', '')
    tipo = request.GET.get('tipo', '')
    alerta = request.GET.get('alerta', '')
    
    if busca:
        veiculos = veiculos.filter(
            Q(placa__icontains=busca) |
            Q(marca__icontains=busca) |
            Q(modelo__icontains=busca)
        )
    
    if status:
        if status == 'manutencao':
            veiculos = veiculos.filter(status='MANUTENCAO')
        else:
            veiculos = veiculos.filter(status=status.upper())
    
    if tipo:
        veiculos = veiculos.filter(tipo_veiculo=tipo.upper())
        
    if alerta == 'vistoria':
        veiculos = veiculos.filter(proxima_vistoria__lt=date.today())
    elif alerta == 'seguro':
        veiculos = veiculos.filter(validade_seguro__lt=date.today())
    
    veiculos = veiculos.order_by('placa')
    
    # Paginação
    paginator = Paginator(veiculos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Veículos',
        'page_obj': page_obj,
        'busca': busca,
        'status': status,
        'tipo': tipo,
        'alerta': alerta,
        'tipos_veiculo': Veiculo.TIPO_VEICULO_CHOICES,
        'status_choices': Veiculo.STATUS_CHOICES,
    }
    return render(request, 'transporte/veiculo_list.html', context)

@login_required
def veiculo_create(request):
    """Criar novo veículo"""
    form = VeiculoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        veiculo = form.save(commit=False)
        veiculo.usuario_cadastro = request.user
        veiculo.save()
        registrar(request, 'CRIAR', veiculo, 'Novo veículo cadastrado')
        messages.success(request, f'Veículo "{veiculo.placa}" criado com sucesso!')
        return redirect('transporte:veiculo_detail', pk=veiculo.pk)
    return form_page(request, form, 'Novo Veículo', reverse('transporte:veiculo_list'),
                     icon='fa-bus', submit_label='Cadastrar veículo')


@login_required
def veiculo_edit(request, pk):
    """Editar veículo"""
    veiculo = get_object_or_404(Veiculo, pk=pk)
    form = VeiculoForm(request.POST or None, instance=veiculo)
    if request.method == 'POST' and form.is_valid():
        form.save()
        registrar(request, 'EDITAR', veiculo, 'Veículo atualizado')
        messages.success(request, f'Veículo "{veiculo.placa}" atualizado com sucesso!')
        return redirect('transporte:veiculo_detail', pk=veiculo.pk)
    return form_page(request, form, 'Editar Veículo', reverse('transporte:veiculo_detail', args=[pk]),
                     icon='fa-bus', subtitle=f'{veiculo.placa} · {veiculo.marca} {veiculo.modelo}')


@login_required
def manutencao_create(request, veiculo_pk):
    """Registrar manutenção para um veículo"""
    veiculo = get_object_or_404(Veiculo, pk=veiculo_pk)
    form = ManutencaoVeiculoForm(request.POST or None, veiculo=veiculo)
    if request.method == 'POST' and form.is_valid():
        manutencao = form.save(commit=False)
        manutencao.usuario_cadastro = request.user
        manutencao.save()
        messages.success(request, 'Manutenção registrada com sucesso!')
        return redirect('transporte:veiculo_detail', pk=veiculo.pk)
    return form_page(request, form, 'Registrar Manutenção', reverse('transporte:veiculo_detail', args=[veiculo.pk]),
                     icon='fa-wrench', subtitle=f'Veículo {veiculo.placa}', submit_label='Registrar')

@login_required
def veiculo_detail(request, pk):
    """
    Detalhes do veículo
    """
    veiculo = get_object_or_404(Veiculo, pk=pk)
    
    # Rotas do veículo
    rotas_ativas = Rota.objects.filter(veiculo=veiculo, ativa=True)
    
    # Manutenções
    manutencoes = ManutencaoVeiculo.objects.filter(
        veiculo=veiculo
    ).order_by('-data_agendamento')[:10]
    
    # Viagens recentes
    viagens_recentes = RegistroViagem.objects.filter(
        veiculo=veiculo
    ).select_related('rota', 'motorista').order_by('-data_viagem')[:10]
    
    # Estatísticas
    total_viagens = RegistroViagem.objects.filter(veiculo=veiculo).count()
    total_km = km_percorridos(RegistroViagem.objects.filter(veiculo=veiculo))
    
    context = {
        'title': f'Veículo: {veiculo.placa}',
        'veiculo': veiculo,
        'rotas_ativas': rotas_ativas,
        'manutencoes': manutencoes,
        'viagens_recentes': viagens_recentes,
        'total_viagens': total_viagens,
        'total_km': total_km,
    }
    return render(request, 'transporte/veiculo_detail.html', context)

# ================ ROTAS ================

@login_required
def rota_list(request):
    """
    Lista de rotas
    """
    rotas = Rota.objects.select_related('veiculo', 'motorista').annotate(
        alunos_ativos=Count('alunos_rota', filter=Q(alunos_rota__ativo=True))
    )
    
    # Filtros
    busca = request.GET.get('busca', '')
    turno = request.GET.get('turno', '')
    ativa = request.GET.get('ativa', '')
    
    if busca:
        rotas = rotas.filter(nome__icontains=busca)
    
    if turno:
        rotas = rotas.filter(turno=turno.upper())
        
    if ativa == 'sim':
        rotas = rotas.filter(ativa=True)
    elif ativa == 'nao':
        rotas = rotas.filter(ativa=False)
    
    rotas = rotas.order_by('nome')
    
    # Paginação
    paginator = Paginator(rotas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Rotas',
        'page_obj': page_obj,
        'busca': busca,
        'turno': turno,
        'ativa': ativa,
        'turnos': Rota.TURNO_CHOICES,
    }
    return render(request, 'transporte/rota_list.html', context)

@login_required
def rota_create(request):
    """Criar nova rota"""
    form = RotaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        rota = form.save(commit=False)
        rota.usuario_cadastro = request.user
        rota.save()
        registrar(request, 'CRIAR', rota, 'Nova rota cadastrada')
        messages.success(request, f'Rota "{rota.nome}" criada. Cadastre agora os pontos de parada.')
        return redirect('transporte:rota_detail', pk=rota.pk)
    return form_page(request, form, 'Nova Rota', reverse('transporte:rota_list'),
                     icon='fa-route', submit_label='Criar rota')


@login_required
def rota_edit(request, pk):
    """Editar rota"""
    rota = get_object_or_404(Rota, pk=pk)
    form = RotaForm(request.POST or None, instance=rota)
    if request.method == 'POST' and form.is_valid():
        form.save()
        registrar(request, 'EDITAR', rota, 'Rota atualizada')
        messages.success(request, f'Rota "{rota.nome}" atualizada com sucesso!')
        return redirect('transporte:rota_detail', pk=rota.pk)
    return form_page(request, form, 'Editar Rota', reverse('transporte:rota_detail', args=[pk]),
                     icon='fa-route', subtitle=rota.nome)


@login_required
def ponto_create(request, rota_pk):
    """Cadastrar ponto de parada na rota"""
    rota = get_object_or_404(Rota, pk=rota_pk)
    form = PontoParadaForm(request.POST or None, rota=rota)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ponto de parada cadastrado com sucesso!')
        return redirect('transporte:rota_detail', pk=rota.pk)
    return form_page(request, form, 'Novo Ponto de Parada', reverse('transporte:rota_detail', args=[rota.pk]),
                     icon='fa-map-marker-alt', subtitle=f'Rota {rota.nome}', submit_label='Cadastrar ponto')


@login_required
def ponto_edit(request, pk):
    """Editar ponto de parada"""
    ponto = get_object_or_404(PontoParada, pk=pk)
    form = PontoParadaForm(request.POST or None, instance=ponto, rota=ponto.rota)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ponto de parada atualizado com sucesso!')
        return redirect('transporte:rota_detail', pk=ponto.rota_id)
    return form_page(request, form, 'Editar Ponto de Parada', reverse('transporte:rota_detail', args=[ponto.rota_id]),
                     icon='fa-map-marker-alt', subtitle=ponto.nome)

@login_required
def rota_detail(request, pk):
    """
    Detalhes da rota
    """
    rota = get_object_or_404(Rota, pk=pk)
    
    # Pontos de parada
    pontos = PontoParada.objects.filter(rota=rota, ativo=True).order_by('ordem')
    
    # Alunos da rota
    alunos_rota = AlunoTransporte.objects.filter(
        rota=rota, ativo=True
    ).select_related('aluno', 'ponto_embarque', 'ponto_desembarque')
    
    # Viagens recentes
    viagens_recentes = RegistroViagem.objects.filter(
        rota=rota
    ).select_related('motorista', 'veiculo').order_by('-data_viagem')[:10]
    
    context = {
        'title': f'Rota: {rota.nome}',
        'rota': rota,
        'pontos': pontos,
        'alunos_rota': alunos_rota,
        'viagens_recentes': viagens_recentes,
        'total_pontos': pontos.count(),
        'total_alunos': alunos_rota.count(),
    }
    return render(request, 'transporte/rota_detail.html', context)

# ================ ALUNOS NO TRANSPORTE ================

@login_required
def aluno_transporte_list(request):
    """
    Lista de alunos no transporte
    """
    alunos_transporte = AlunoTransporte.objects.select_related(
        'aluno', 'rota', 'ponto_embarque', 'ponto_desembarque'
    )
    
    # Filtros
    busca = request.GET.get('busca', '')
    rota_id = request.GET.get('rota', '')
    situacao = request.GET.get('situacao', '')
    
    if busca:
        alunos_transporte = alunos_transporte.filter(
            Q(aluno__nome__icontains=busca) |
            Q(responsavel_nome__icontains=busca)
        )
    
    if rota_id:
        alunos_transporte = alunos_transporte.filter(rota_id=rota_id)
        
    if situacao:
        alunos_transporte = alunos_transporte.filter(situacao=situacao.upper())
    
    alunos_transporte = alunos_transporte.order_by('aluno__nome')
    
    # Paginação
    paginator = Paginator(alunos_transporte, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Rotas para filtro
    rotas_ativas = Rota.objects.filter(ativa=True).order_by('nome')
    
    context = {
        'title': 'Alunos no Transporte',
        'page_obj': page_obj,
        'busca': busca,
        'rota_id': rota_id,
        'situacao': situacao,
        'rotas_ativas': rotas_ativas,
        'situacoes': AlunoTransporte.SITUACAO_CHOICES,
    }
    return render(request, 'transporte/aluno_transporte_list.html', context)


@login_required
def aluno_transporte_create(request, rota_pk):
    """Vincular aluno a uma rota"""
    rota = get_object_or_404(Rota, pk=rota_pk)
    detalhe_url = reverse('transporte:rota_detail', args=[rota.pk])
    if not rota.pontos.filter(ativo=True).exists():
        messages.error(request, 'Cadastre ao menos um ponto de parada antes de vincular alunos.')
        return redirect(detalhe_url)
    form = AlunoTransporteForm(request.POST or None, rota=rota, initial={'data_inicio': date.today()})
    if request.method == 'POST' and form.is_valid():
        vinculo = form.save(commit=False)
        vinculo.usuario_cadastro = request.user
        vinculo.save()
        registrar(request, 'CRIAR', vinculo.aluno, f'Aluno vinculado à rota {rota.nome}')
        messages.success(request, f'{vinculo.aluno.nome} vinculado(a) à rota {rota.nome}.')
        return redirect(detalhe_url)
    return form_page(request, form, 'Vincular Aluno à Rota', detalhe_url,
                     icon='fa-user-plus', subtitle=rota.nome, submit_label='Vincular')


@login_required
def aluno_transporte_edit(request, pk):
    """Editar vínculo do aluno com o transporte"""
    vinculo = get_object_or_404(AlunoTransporte.objects.select_related('aluno', 'rota'), pk=pk)
    form = AlunoTransporteForm(request.POST or None, instance=vinculo)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Dados de transporte do aluno atualizados.')
        return redirect('transporte:rota_detail', pk=vinculo.rota_id)
    return form_page(request, form, 'Editar Transporte do Aluno', reverse('transporte:rota_detail', args=[vinculo.rota_id]),
                     icon='fa-user-edit', subtitle=f'{vinculo.aluno.nome} · {vinculo.rota.nome}')


@login_required
def viagem_create(request):
    """Registrar uma viagem realizada"""
    rota = Rota.objects.filter(pk=request.GET.get('rota')).select_related('motorista', 'veiculo').first()
    inicial = {'data_viagem': date.today()}
    if rota:
        inicial.update({'rota': rota.pk, 'motorista': rota.motorista_id, 'veiculo': rota.veiculo_id})
    form = RegistroViagemForm(request.POST or None, initial=inicial)
    if request.method == 'POST' and form.is_valid():
        viagem = form.save(commit=False)
        viagem.usuario_cadastro = request.user
        viagem.save()
        if viagem.km_final and viagem.km_final > (viagem.veiculo.km_atual or 0):
            viagem.veiculo.km_atual = viagem.km_final
            viagem.veiculo.save(update_fields=['km_atual'])
        messages.success(request, 'Viagem registrada com sucesso!')
        return redirect('transporte:rota_detail', pk=viagem.rota_id)
    cancelar = reverse('transporte:rota_detail', args=[rota.pk]) if rota else reverse('transporte:transporte_home')
    return form_page(request, form, 'Registrar Viagem', cancelar, icon='fa-road', submit_label='Registrar viagem')

@login_required
def relatorio_transporte(request):
    """
    Relatórios do transporte escolar
    """
    # Estatísticas gerais por período
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    
    # Viagens no mês
    viagens_mes = RegistroViagem.objects.filter(
        data_viagem__gte=inicio_mes
    ).count()
    
    # KM percorridos no mês
    km_mes = km_percorridos(RegistroViagem.objects.filter(data_viagem__gte=inicio_mes))
    
    # Alunos transportados no mês
    alunos_mes = RegistroViagem.objects.filter(
        data_viagem__gte=inicio_mes
    ).aggregate(total=Sum('alunos_transportados'))['total'] or 0
    
    # Rotas por turno
    rotas_por_turno = {}
    for turno_codigo, turno_nome in Rota.TURNO_CHOICES:
        rotas_por_turno[turno_nome] = Rota.objects.filter(
            turno=turno_codigo, ativa=True
        ).count()
    
    # Veículos por tipo
    veiculos_por_tipo = {}
    for tipo_codigo, tipo_nome in Veiculo.TIPO_VEICULO_CHOICES:
        veiculos_por_tipo[tipo_nome] = Veiculo.objects.filter(
            tipo_veiculo=tipo_codigo, status='ATIVO'
        ).count()
    
    context = {
        'title': 'Relatórios de Transporte',
        'viagens_mes': viagens_mes,
        'km_mes': km_mes,
        'alunos_mes': alunos_mes,
        'rotas_por_turno': rotas_por_turno,
        'veiculos_por_tipo': veiculos_por_tipo,
        'mes_atual': f'{MESES_PT[inicio_mes.month - 1]} {inicio_mes.year}',
    }
    return render(request, 'transporte/relatorio_transporte.html', context)

# ================ AJAX/API ENDPOINTS ================

@login_required
def ajax_pontos_rota(request, rota_id):
    """
    Retorna pontos de uma rota via AJAX
    """
    pontos = PontoParada.objects.filter(
        rota_id=rota_id, ativo=True
    ).values('id', 'nome', 'ordem').order_by('ordem')
    
    return JsonResponse({'pontos': list(pontos)})
