from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import date, datetime, timedelta
from .models import (
    Motorista, Veiculo, Rota, PontoParada, AlunoTransporte, 
    RegistroViagem, ManutencaoVeiculo
)
from .forms import (
    MotoristaForm, VeiculoForm, RotaForm, PontoParadaForm, 
    AlunoTransporteForm, RegistroViagemForm, ManutencaoVeiculoForm
)

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
            'link': '/transporte/motoristas/?alerta=cnh'
        })
    
    # Veículos em manutenção
    veiculos_manutencao = Veiculo.objects.filter(status='MANUTENCAO').count()
    if veiculos_manutencao > 0:
        alertas.append({
            'tipo': 'info',
            'titulo': 'Veículos em Manutenção',
            'mensagem': f'{veiculos_manutencao} veículo(s) em manutenção',
            'icone': 'fa-wrench',
            'link': '/transporte/veiculos/?status=manutencao'
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
            'link': '/transporte/veiculos/?alerta=vistoria'
        })
    
    # Rotas mais utilizadas
    rotas_populares = Rota.objects.filter(ativa=True).annotate(
        total_alunos=Count('alunos_rota', filter=Q(alunos_rota__ativo=True))
    ).order_by('-total_alunos')[:5]
    
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
    """
    Criar novo motorista
    """
    if request.method == 'POST':
        form = MotoristaForm(request.POST)
        if form.is_valid():
            motorista = form.save(commit=False)
            motorista.usuario_cadastro = request.user
            motorista.save()
            messages.success(request, f'Motorista "{motorista.nome}" criado com sucesso!')
            return redirect('transporte:motorista_detail', pk=motorista.pk)
    else:
        form = MotoristaForm()
    
    context = {
        'title': 'Novo Motorista',
        'form': form,
        'action': 'Criar'
    }
    return render(request, 'transporte/motorista_form.html', context)

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
    km_percorridos = RegistroViagem.objects.filter(
        motorista=motorista
    ).aggregate(total_km=Sum('km_final') - Sum('km_inicial'))['total_km'] or 0
    
    context = {
        'title': f'Motorista: {motorista.nome}',
        'motorista': motorista,
        'rotas_ativas': rotas_ativas,
        'viagens_recentes': viagens_recentes,
        'total_viagens': total_viagens,
        'km_percorridos': km_percorridos,
    }
    return render(request, 'transporte/motorista_detail.html', context)

@login_required
def motorista_edit(request, pk):
    """
    Editar motorista
    """
    motorista = get_object_or_404(Motorista, pk=pk)
    
    if request.method == 'POST':
        form = MotoristaForm(request.POST, instance=motorista)
        if form.is_valid():
            form.save()
            messages.success(request, f'Motorista "{motorista.nome}" atualizado com sucesso!')
            return redirect('transporte:motorista_detail', pk=motorista.pk)
    else:
        form = MotoristaForm(instance=motorista)
    
    context = {
        'title': f'Editar Motorista: {motorista.nome}',
        'form': form,
        'motorista': motorista,
        'action': 'Salvar Alterações'
    }
    return render(request, 'transporte/motorista_form.html', context)

@login_required
def motorista_delete(request, pk):
    """
    Deletar motorista
    """
    motorista = get_object_or_404(Motorista, pk=pk)
    
    if request.method == 'POST':
        # Verificar se tem vínculos ativos
        rotas_ativas = Rota.objects.filter(motorista=motorista, ativa=True).count()
        if rotas_ativas > 0:
            messages.error(request, 'Não é possível excluir motorista com rotas ativas.')
            return redirect('transporte:motorista_detail', pk=pk)
        
        nome_motorista = motorista.nome
        motorista.delete()
        messages.success(request, f'Motorista "{nome_motorista}" excluído com sucesso!')
        return redirect('transporte:motorista_list')
    
    context = {
        'title': f'Excluir Motorista: {motorista.nome}',
        'motorista': motorista,
    }
    return render(request, 'transporte/motorista_confirm_delete.html', context)

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
    """
    Criar novo veículo
    """
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            veiculo = form.save(commit=False)
            veiculo.usuario_cadastro = request.user
            veiculo.save()
            messages.success(request, f'Veículo "{veiculo.placa}" criado com sucesso!')
            return redirect('transporte:veiculo_detail', pk=veiculo.pk)
    else:
        form = VeiculoForm()
    
    context = {
        'title': 'Novo Veículo',
        'form': form,
        'action': 'Criar'
    }
    return render(request, 'transporte/veiculo_form.html', context)

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
    total_km = RegistroViagem.objects.filter(
        veiculo=veiculo
    ).aggregate(total=Sum('km_final') - Sum('km_inicial'))['total'] or 0
    
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
    rotas = Rota.objects.annotate(
        total_alunos=Count('alunos_rota', filter=Q(alunos_rota__ativo=True))
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
    """
    Criar nova rota
    """
    if request.method == 'POST':
        form = RotaForm(request.POST)
        if form.is_valid():
            rota = form.save(commit=False)
            rota.usuario_cadastro = request.user
            rota.save()
            messages.success(request, f'Rota "{rota.nome}" criada com sucesso!')
            return redirect('transporte:rota_detail', pk=rota.pk)
    else:
        form = RotaForm()
    
    context = {
        'title': 'Nova Rota',
        'form': form,
        'action': 'Criar'
    }
    return render(request, 'transporte/rota_form.html', context)

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
    km_mes = RegistroViagem.objects.filter(
        data_viagem__gte=inicio_mes
    ).aggregate(total=Sum('km_final') - Sum('km_inicial'))['total'] or 0
    
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
        'mes_atual': inicio_mes.strftime('%B %Y'),
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

@login_required
def ajax_alunos_sem_transporte(request):
    """
    Retorna alunos que não têm transporte ativo
    """
    from alunos.models import Aluno
    
    # Alunos que não estão em nenhuma rota ativa
    alunos_com_transporte = AlunoTransporte.objects.filter(
        ativo=True
    ).values_list('aluno_id', flat=True)
    
    alunos_sem_transporte = Aluno.objects.exclude(
        id__in=alunos_com_transporte
    ).values('id', 'nome', 'codigo').order_by('nome')
    
    return JsonResponse({'alunos': list(alunos_sem_transporte)})