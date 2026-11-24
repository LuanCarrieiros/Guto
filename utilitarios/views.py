from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from turma.forms import TipoAvaliacaoForm
from turma.models import TipoAvaliacao
from .acesso import registrar_auditoria
from .forms import (
    MODULOS_SISTEMA, BloqueioFuncionalidadeForm, ConfiguracaoSistemaForm, DadoAdicionalForm,
    GrupoAcessoForm, InstituicaoForm, PerfilUsuarioForm, SolicitacaoTransferenciaForm, UsuarioForm,
)
from .models import (
    BloqueioFuncionalidade, ConfiguracaoSistema, DadoAdicional, GrupoAcesso, Instituicao,
    PermissaoGrupo, RegistroAuditoria, SolicitacaoTransferencia,
)

# O módulo Utilitários é restrito à administração do sistema
apenas_administradores = user_passes_test(lambda u: u.is_active and (u.is_superuser or u.is_staff))


def administracao(view):
    return login_required(apenas_administradores(view))


@administracao
def dashboard_utilitarios(request):
    context = {
        'total_usuarios': User.objects.count(),
        'usuarios_ativos': User.objects.filter(is_active=True).count(),
        'total_grupos': GrupoAcesso.objects.count(),
        'total_instituicoes': Instituicao.objects.count(),
        'total_solicitacoes': SolicitacaoTransferencia.objects.filter(status='PENDENTE').count(),
        'bloqueios_ativos': BloqueioFuncionalidade.objects.filter(ativo=True).count(),
        'registros_hoje': RegistroAuditoria.objects.filter(data_acao__date=timezone.localdate()).count(),
        'ultimos_registros': RegistroAuditoria.objects.select_related('usuario')[:8],
    }
    return render(request, 'utilitarios/dashboard.html', context)


# ============================== USUÁRIOS ==============================

@administracao
def gerenciar_usuarios(request):
    query = request.GET.get('q', '').strip()
    grupo = request.GET.get('grupo', '')
    status = request.GET.get('status', '')

    usuarios = User.objects.prefetch_related('groups').order_by('first_name', 'username')
    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) |
            Q(last_name__icontains=query) | Q(email__icontains=query)
        )
    if grupo:
        usuarios = usuarios.filter(groups__name=grupo)
    if status == 'ativo':
        usuarios = usuarios.filter(is_active=True)
    elif status == 'inativo':
        usuarios = usuarios.filter(is_active=False)

    page_obj = Paginator(usuarios, 20).get_page(request.GET.get('page'))
    context = {
        'page_obj': page_obj,
        'grupos': GrupoAcesso.objects.order_by('nome'),
        'query': query,
        'grupo_selecionado': grupo,
        'status': status,
    }
    return render(request, 'utilitarios/gerenciar_usuarios.html', context)


def _salvar_usuario(request, usuario=None):
    """Cria ou edita um usuário com seu perfil complementar."""
    perfil = getattr(usuario, 'perfilusuario', None) if usuario else None
    form = UsuarioForm(request.POST or None, instance=usuario)
    perfil_form = PerfilUsuarioForm(request.POST or None, instance=perfil, prefix='perfil')

    if request.method == 'POST' and form.is_valid() and perfil_form.is_valid():
        salvar_perfil = bool(perfil_form.instance.pk) or perfil_form.has_data()
        if salvar_perfil and not perfil_form.cleaned_data.get('cpf'):
            perfil_form.add_error('cpf', 'Informe o CPF para salvar os dados complementares.')
        else:
            novo = form.instance.pk is None
            with transaction.atomic():
                usuario = form.save()
                if salvar_perfil:
                    perfil_obj = perfil_form.save(commit=False)
                    perfil_obj.user = usuario
                    if not perfil_obj.pk:
                        perfil_obj.usuario_criacao = request.user
                    perfil_obj.save()
            messages.success(request, f'Usuário "{usuario.username}" {"criado" if novo else "atualizado"} com sucesso!')
            return redirect('utilitarios:gerenciar_usuarios'), None

    contexto = {
        'form': form,
        'perfil_form': perfil_form,
        'usuario_editado': usuario,
    }
    return None, contexto


@administracao
def criar_usuario(request):
    resposta, contexto = _salvar_usuario(request)
    if resposta:
        return resposta
    contexto['title'] = 'Novo Usuário'
    return render(request, 'utilitarios/usuario_form.html', contexto)


@administracao
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    resposta, contexto = _salvar_usuario(request, usuario)
    if resposta:
        return resposta
    contexto['title'] = f'Editar Usuário - {usuario.username}'
    return render(request, 'utilitarios/usuario_form.html', contexto)


# ============================== GRUPOS DE ACESSO ==============================

@administracao
def gerenciar_grupos(request):
    form = GrupoAcessoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        grupo = form.save(commit=False)
        grupo.usuario_criacao = request.user
        grupo.save()
        Group.objects.get_or_create(name=grupo.nome)
        messages.success(request, f'Grupo "{grupo.nome}" criado. Defina agora as permissões do grupo.')
        return redirect('utilitarios:editar_grupo', grupo_id=grupo.pk)

    grupos = GrupoAcesso.objects.annotate(total_permissoes=Count('permissoes')).order_by('nome')
    usuarios_por_grupo = dict(
        Group.objects.annotate(total=Count('user')).values_list('name', 'total')
    )
    for grupo in grupos:
        grupo.total_usuarios = usuarios_por_grupo.get(grupo.nome, 0)
    return render(request, 'utilitarios/gerenciar_grupos.html', {'grupos': grupos, 'form': form})


@administracao
def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(GrupoAcesso, id=grupo_id)
    nome_anterior = grupo.nome
    form = GrupoAcessoForm(request.POST or None, instance=grupo)
    campos = ['visualizar', 'incluir', 'alterar', 'excluir', 'imprimir']

    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            grupo = form.save()
            # Mantém o grupo do Django (usado para vincular usuários) com o mesmo nome
            auth_group = Group.objects.filter(name=nome_anterior).first()
            if auth_group:
                auth_group.name = grupo.nome
                auth_group.save()
            else:
                Group.objects.get_or_create(name=grupo.nome)

            for codigo, _ in MODULOS_SISTEMA:
                valores = {c: request.POST.get(f'{codigo}__{c}') == 'on' for c in campos}
                if request.POST.get(f'{codigo}__restringir') == 'on':
                    PermissaoGrupo.objects.update_or_create(
                        grupo=grupo, modulo=codigo, submenu=None, funcionalidade=None, defaults=valores
                    )
                else:
                    PermissaoGrupo.objects.filter(grupo=grupo, modulo=codigo).delete()
        messages.success(request, f'Grupo "{grupo.nome}" atualizado com sucesso!')
        return redirect('utilitarios:gerenciar_grupos')

    permissoes = {p.modulo: p for p in grupo.permissoes.filter(submenu__isnull=True, funcionalidade__isnull=True)}
    matriz = []
    for codigo, nome in MODULOS_SISTEMA:
        permissao = permissoes.get(codigo)
        matriz.append({
            'codigo': codigo,
            'nome': nome,
            'restringir': permissao is not None,
            'valores': [(c, getattr(permissao, c) if permissao else True) for c in campos],
        })
    context = {
        'grupo': grupo,
        'form': form,
        'matriz': matriz,
        'campos': campos,
        'usuarios': User.objects.filter(groups__name=grupo.nome).order_by('username'),
    }
    return render(request, 'utilitarios/editar_grupo.html', context)


# ============================== INSTITUIÇÕES ==============================

@administracao
def instituicoes(request):
    form = InstituicaoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        instituicao = form.save()
        messages.success(request, f'Instituição "{instituicao.nome}" cadastrada com sucesso!')
        return redirect('utilitarios:instituicoes')
    lista = Instituicao.objects.select_related('instituicao_pai').order_by('nome')
    return render(request, 'utilitarios/instituicoes.html', {'instituicoes': lista, 'form': form})


@administracao
def editar_instituicao(request, pk):
    instituicao = get_object_or_404(Instituicao, pk=pk)
    form = InstituicaoForm(request.POST or None, instance=instituicao)
    form.fields['instituicao_pai'].queryset = Instituicao.objects.exclude(pk=pk)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Instituição atualizada com sucesso!')
        return redirect('utilitarios:instituicoes')
    return render(request, 'generic/form.html', {
        'form': form,
        'title': 'Editar Instituição',
        'subtitle': instituicao.nome,
        'icon': 'fa-school',
        'cancel_url': reverse('utilitarios:instituicoes'),
    })


# ============================== CONFIGURAÇÕES ==============================

@administracao
def configuracoes_sistema(request):
    editar_id = request.GET.get('editar')
    instancia = get_object_or_404(ConfiguracaoSistema, pk=editar_id) if editar_id else None
    if instancia and not instancia.editavel:
        messages.error(request, 'Esta configuração não pode ser alterada.')
        return redirect('utilitarios:configuracoes_sistema')

    form = ConfiguracaoSistemaForm(request.POST or None, instance=instancia)
    if request.method == 'POST' and form.is_valid():
        config = form.save(commit=False)
        config.usuario_atualizacao = request.user
        config.save()
        messages.success(request, f'Configuração "{config.chave}" salva com sucesso!')
        return redirect('utilitarios:configuracoes_sistema')

    context = {
        'configuracoes': ConfiguracaoSistema.objects.select_related('usuario_atualizacao'),
        'form': form,
        'editando': instancia,
    }
    return render(request, 'utilitarios/configuracoes_sistema.html', context)


# ============================== DADOS ADICIONAIS ==============================

@administracao
def dados_adicionais(request):
    editar_id = request.GET.get('editar')
    instancia = get_object_or_404(DadoAdicional, pk=editar_id) if editar_id else None
    form = DadoAdicionalForm(request.POST or None, instance=instancia)
    if request.method == 'POST' and form.is_valid():
        dado = form.save(commit=False)
        if not dado.pk:
            dado.usuario_criacao = request.user
        dado.save()
        messages.success(request, f'Campo adicional "{dado.rotulo}" salvo com sucesso!')
        return redirect('utilitarios:dados_adicionais')

    context = {
        'dados': DadoAdicional.objects.annotate(total_valores=Count('valordadoadicional')),
        'form': form,
        'editando': instancia,
    }
    return render(request, 'utilitarios/dados_adicionais.html', context)


# ============================== AUDITORIA ==============================

@administracao
def auditoria(request):
    registros = RegistroAuditoria.objects.select_related('usuario')

    filtros = {
        'acao': request.GET.get('acao', ''),
        'usuario': request.GET.get('usuario', ''),
        'tela': request.GET.get('tela', ''),
        'data_inicio': request.GET.get('data_inicio', ''),
        'data_fim': request.GET.get('data_fim', ''),
    }
    if filtros['acao']:
        registros = registros.filter(acao=filtros['acao'])
    if filtros['usuario']:
        registros = registros.filter(usuario_id=filtros['usuario'])
    if filtros['tela']:
        registros = registros.filter(tela=filtros['tela'])
    if filtros['data_inicio']:
        registros = registros.filter(data_acao__date__gte=filtros['data_inicio'])
    if filtros['data_fim']:
        registros = registros.filter(data_acao__date__lte=filtros['data_fim'])

    context = {
        'page_obj': Paginator(registros, 50).get_page(request.GET.get('page')),
        'usuarios': User.objects.order_by('username'),
        'acoes': RegistroAuditoria.ACAO_CHOICES,
        'telas': RegistroAuditoria.objects.order_by('tela').values_list('tela', flat=True).distinct(),
        'filtros': filtros,
    }
    return render(request, 'utilitarios/auditoria.html', context)


# ============================== TRANSFERÊNCIAS ==============================

@administracao
def solicitacoes_transferencia(request):
    status_filter = request.GET.get('status', '')
    busca = request.GET.get('q', '').strip()
    solicitacoes = SolicitacaoTransferencia.objects.select_related(
        'aluno', 'escola_origem', 'escola_destino', 'usuario_solicitacao', 'usuario_processamento'
    )
    if status_filter:
        solicitacoes = solicitacoes.filter(status=status_filter)
    if busca:
        solicitacoes = solicitacoes.filter(aluno__nome__icontains=busca)

    form = SolicitacaoTransferenciaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        solicitacao = form.save(commit=False)
        solicitacao.usuario_solicitacao = request.user
        solicitacao.save()
        messages.success(request, f'Solicitação de transferência de {solicitacao.aluno.nome} registrada.')
        return redirect('utilitarios:solicitacoes_transferencia')

    context = {
        'page_obj': Paginator(solicitacoes, 20).get_page(request.GET.get('page')),
        'status_filter': status_filter,
        'busca': busca,
        'status_choices': SolicitacaoTransferencia.STATUS_CHOICES,
        'contagem': dict(SolicitacaoTransferencia.objects.values_list('status').annotate(total=Count('id'))),
        'form': form,
        'tem_instituicoes': Instituicao.objects.filter(ativo=True).count() >= 2,
    }
    return render(request, 'utilitarios/solicitacoes_transferencia.html', context)


@administracao
@require_POST
def processar_transferencia(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoTransferencia, id=solicitacao_id)
    if solicitacao.status != 'PENDENTE':
        messages.error(request, 'Esta solicitação já foi processada.')
        return redirect('utilitarios:solicitacoes_transferencia')

    acao = request.POST.get('acao')
    novo_status = {'aceitar': 'ACEITA', 'rejeitar': 'REJEITADA'}.get(acao)
    if not novo_status:
        messages.error(request, 'Ação inválida.')
        return redirect('utilitarios:solicitacoes_transferencia')

    solicitacao.status = novo_status
    solicitacao.usuario_processamento = request.user
    solicitacao.data_processamento = timezone.now()
    observacoes = request.POST.get('observacoes', '').strip()
    if observacoes:
        solicitacao.observacoes = observacoes
    solicitacao.save()

    if novo_status == 'ACEITA':
        messages.success(request, f'Transferência de {solicitacao.aluno.nome} aceita.')
    else:
        messages.warning(request, f'Transferência de {solicitacao.aluno.nome} rejeitada.')
    return redirect('utilitarios:solicitacoes_transferencia')


# ============================== TIPOS DE AVALIAÇÃO ==============================

@administracao
def tipos_avaliacao(request):
    editar_id = request.GET.get('editar')
    instancia = get_object_or_404(TipoAvaliacao, pk=editar_id) if editar_id else None
    form = TipoAvaliacaoForm(request.POST or None, instance=instancia)
    if request.method == 'POST' and form.is_valid():
        tipo = form.save()
        messages.success(request, f'Tipo de avaliação "{tipo.nome}" salvo com sucesso!')
        return redirect('utilitarios:tipos_avaliacao')

    context = {
        'tipos': TipoAvaliacao.objects.annotate(total_avaliacoes=Count('avaliacao')).order_by('nome'),
        'form': form,
        'editando': instancia,
    }
    return render(request, 'utilitarios/tipos_avaliacao.html', context)


# ============================== BLOQUEIOS ==============================

@administracao
def bloqueios_funcionalidade(request):
    form = BloqueioFuncionalidadeForm(
        request.POST or None,
        initial={'data_inicio': timezone.localtime().strftime('%Y-%m-%dT%H:%M'), 'ativo': True},
    )
    if request.method == 'POST' and form.is_valid():
        bloqueio = form.save(commit=False)
        bloqueio.usuario_criacao = request.user
        bloqueio.save()
        registrar_auditoria(request, 'CREATE', 'utilitarios', 'Bloqueio de funcionalidade', str(bloqueio))
        messages.success(request, 'Bloqueio criado com sucesso!')
        return redirect('utilitarios:bloqueios_funcionalidade')

    nomes_modulos = dict(MODULOS_SISTEMA)
    bloqueios = list(BloqueioFuncionalidade.objects.select_related('usuario_criacao'))
    agora = timezone.now()
    for b in bloqueios:
        b.nome_modulo = nomes_modulos.get(b.modulo, b.modulo)
        b.vigente = b.ativo and b.data_inicio <= agora and (b.data_fim is None or b.data_fim >= agora)
    return render(request, 'utilitarios/bloqueios_funcionalidade.html', {'bloqueios': bloqueios, 'form': form})


@administracao
@require_POST
def alternar_bloqueio(request, pk):
    bloqueio = get_object_or_404(BloqueioFuncionalidade, pk=pk)
    bloqueio.ativo = not bloqueio.ativo
    bloqueio.save(update_fields=['ativo'])
    messages.success(request, f'Bloqueio {"reativado" if bloqueio.ativo else "desativado"}.')
    return redirect('utilitarios:bloqueios_funcionalidade')
