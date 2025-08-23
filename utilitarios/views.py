from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .models import (
    GrupoAcesso, Instituicao, PerfilUsuario, AssociacaoUsuarioInstituicao,
    ConfiguracaoSistema, DadoAdicional, ValorDadoAdicional, RegistroAuditoria,
    SolicitacaoTransferencia, PermissaoGrupo, BloqueioFuncionalidade,
    MatriculaRapida, CabecalhoRelatorio, TipoAvaliacao
)


@login_required
def dashboard_utilitarios(request):
    context = {
        'total_usuarios': User.objects.count(),
        'total_grupos': GrupoAcesso.objects.count(),
        'total_instituicoes': Instituicao.objects.count(),
        'total_solicitacoes': SolicitacaoTransferencia.objects.filter(status='PENDENTE').count(),
    }
    return render(request, 'utilitarios/dashboard.html', context)


@login_required
def gerenciar_usuarios(request):
    query = request.GET.get('q', '')
    grupo_id = request.GET.get('grupo', '')
    
    usuarios = User.objects.select_related('perfilusuario').all()
    
    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    if grupo_id:
        usuarios = usuarios.filter(perfilusuario__grupo_acesso_id=grupo_id)
    
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    grupos = GrupoAcesso.objects.all()
    
    context = {
        'usuarios': page_obj,
        'grupos': grupos,
        'query': query,
        'grupo_selecionado': grupo_id,
    }
    return render(request, 'utilitarios/gerenciar_usuarios.html', context)


@login_required
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
    
    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name', '')
        usuario.last_name = request.POST.get('last_name', '')
        usuario.email = request.POST.get('email', '')
        usuario.is_active = request.POST.get('is_active') == 'on'
        usuario.save()
        
        grupo_id = request.POST.get('grupo_acesso')
        if grupo_id:
            perfil.grupo_acesso_id = grupo_id
        
        perfil.telefone = request.POST.get('telefone', '')
        perfil.cargo = request.POST.get('cargo', '')
        perfil.observacoes = request.POST.get('observacoes', '')
        perfil.save()
        
        RegistroAuditoria.objects.create(
            usuario=request.user,
            acao='ALTERAR_USUARIO',
            detalhes=f'Usuário {usuario.username} alterado',
            ip_origem=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, 'Usuário atualizado com sucesso!')
        return redirect('utilitarios:gerenciar_usuarios')
    
    grupos = GrupoAcesso.objects.all()
    instituicoes = Instituicao.objects.all()
    
    context = {
        'usuario': usuario,
        'perfil': perfil,
        'grupos': grupos,
        'instituicoes': instituicoes,
    }
    return render(request, 'utilitarios/editar_usuario.html', context)


@login_required
def gerenciar_grupos(request):
    grupos = GrupoAcesso.objects.all().order_by('nome')
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        
        if nome:
            GrupoAcesso.objects.create(
                nome=nome,
                descricao=descricao,
                usuario_criacao=request.user
            )
            messages.success(request, 'Grupo criado com sucesso!')
            return redirect('utilitarios:gerenciar_grupos')
    
    context = {'grupos': grupos}
    return render(request, 'utilitarios/gerenciar_grupos.html', context)


@login_required
def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(GrupoAcesso, id=grupo_id)
    
    if request.method == 'POST':
        grupo.nome = request.POST.get('nome', grupo.nome)
        grupo.descricao = request.POST.get('descricao', grupo.descricao)
        grupo.ativo = request.POST.get('ativo') == 'on'
        grupo.save()
        
        messages.success(request, 'Grupo atualizado com sucesso!')
        return redirect('utilitarios:gerenciar_grupos')
    
    context = {'grupo': grupo}
    return render(request, 'utilitarios/editar_grupo.html', context)


@login_required
def configuracoes_sistema(request):
    configuracoes = ConfiguracaoSistema.objects.all()
    
    if request.method == 'POST':
        chave = request.POST.get('chave')
        valor = request.POST.get('valor')
        descricao = request.POST.get('descricao', '')
        
        if chave and valor:
            config, created = ConfiguracaoSistema.objects.get_or_create(
                chave=chave,
                defaults={
                    'valor': valor,
                    'descricao': descricao,
                    'usuario_criacao': request.user
                }
            )
            if not created:
                config.valor = valor
                config.descricao = descricao
                config.save()
            
            messages.success(request, 'Configuração salva com sucesso!')
            return redirect('utilitarios:configuracoes_sistema')
    
    context = {'configuracoes': configuracoes}
    return render(request, 'utilitarios/configuracoes_sistema.html', context)


@login_required
def dados_adicionais(request):
    dados = DadoAdicional.objects.all().order_by('categoria', 'nome')
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        categoria = request.POST.get('categoria')
        tipo_campo = request.POST.get('tipo_campo')
        obrigatorio = request.POST.get('obrigatorio') == 'on'
        
        if nome and categoria and tipo_campo:
            DadoAdicional.objects.create(
                nome=nome,
                categoria=categoria,
                tipo_campo=tipo_campo,
                obrigatorio=obrigatorio,
                usuario_criacao=request.user
            )
            messages.success(request, 'Campo adicional criado com sucesso!')
            return redirect('utilitarios:dados_adicionais')
    
    context = {'dados': dados}
    return render(request, 'utilitarios/dados_adicionais.html', context)


@login_required
def auditoria(request):
    registros = RegistroAuditoria.objects.all().order_by('-data_acao')
    
    # Filtros
    acao = request.GET.get('acao', '')
    usuario_id = request.GET.get('usuario', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    if acao:
        registros = registros.filter(acao=acao)
    if usuario_id:
        registros = registros.filter(usuario_id=usuario_id)
    if data_inicio:
        registros = registros.filter(data_acao__date__gte=data_inicio)
    if data_fim:
        registros = registros.filter(data_acao__date__lte=data_fim)
    
    paginator = Paginator(registros, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    usuarios = User.objects.all()
    acoes = RegistroAuditoria.objects.values_list('acao', flat=True).distinct()
    
    context = {
        'registros': page_obj,
        'usuarios': usuarios,
        'acoes': acoes,
        'filtros': {
            'acao': acao,
            'usuario': usuario_id,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        }
    }
    return render(request, 'utilitarios/auditoria.html', context)


@login_required
def solicitacoes_transferencia(request):
    solicitacoes = SolicitacaoTransferencia.objects.all().order_by('-data_solicitacao')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        solicitacoes = solicitacoes.filter(status=status_filter)
    
    paginator = Paginator(solicitacoes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'solicitacoes': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'utilitarios/solicitacoes_transferencia.html', context)


@login_required
@require_http_methods(["POST"])
def processar_transferencia(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoTransferencia, id=solicitacao_id)
    acao = request.POST.get('acao')
    observacoes = request.POST.get('observacoes', '')
    
    if acao == 'aprovar':
        solicitacao.status = 'APROVADA'
        solicitacao.usuario_processamento = request.user
        solicitacao.data_processamento = timezone.now()
        solicitacao.observacoes_processamento = observacoes
        messages.success(request, 'Solicitação aprovada com sucesso!')
    elif acao == 'rejeitar':
        solicitacao.status = 'REJEITADA'
        solicitacao.usuario_processamento = request.user
        solicitacao.data_processamento = timezone.now()
        solicitacao.observacoes_processamento = observacoes
        messages.warning(request, 'Solicitação rejeitada!')
    
    solicitacao.save()
    
    RegistroAuditoria.objects.create(
        usuario=request.user,
        acao='PROCESSAR_TRANSFERENCIA',
        detalhes=f'Solicitação #{solicitacao.id} {solicitacao.status.lower()}',
        ip_origem=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return redirect('utilitarios:solicitacoes_transferencia')


@login_required
def tipos_avaliacao(request):
    tipos = TipoAvaliacao.objects.all().order_by('nome')
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        peso = request.POST.get('peso', 1)
        
        if nome:
            TipoAvaliacao.objects.create(
                nome=nome,
                descricao=descricao,
                peso=peso,
                usuario_criacao=request.user
            )
            messages.success(request, 'Tipo de avaliação criado com sucesso!')
            return redirect('utilitarios:tipos_avaliacao')
    
    context = {'tipos': tipos}
    return render(request, 'utilitarios/tipos_avaliacao.html', context)


@login_required
def bloqueios_funcionalidade(request):
    bloqueios = BloqueioFuncionalidade.objects.all().order_by('-data_criacao')
    
    if request.method == 'POST':
        funcionalidade = request.POST.get('funcionalidade')
        motivo = request.POST.get('motivo', '')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        
        if funcionalidade and data_inicio:
            BloqueioFuncionalidade.objects.create(
                funcionalidade=funcionalidade,
                motivo=motivo,
                data_inicio=data_inicio,
                data_fim=data_fim if data_fim else None,
                usuario_criacao=request.user
            )
            messages.success(request, 'Bloqueio criado com sucesso!')
            return redirect('utilitarios:bloqueios_funcionalidade')
    
    context = {'bloqueios': bloqueios}
    return render(request, 'utilitarios/bloqueios_funcionalidade.html', context)