"""
Controle de acesso do GUTO.

Aplica, em todas as requisições dos módulos, as regras cadastradas em Utilitários:
- Bloqueios de funcionalidade (RF2103): impedem incluir/alterar/excluir em um módulo.
- Permissões de grupo (RF2102): definem o que cada grupo de acesso pode fazer em cada módulo.

Superusuários não são afetados, e o próprio módulo Utilitários nunca é bloqueado
(para que um administrador sempre consiga desfazer um bloqueio).
"""
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone

from guto_system.utils import ano_atual

MODULOS_LIVRES = {None, '', 'admin', 'dashboard', 'utilitarios'}

PALAVRAS_EXCLUIR = ('delete', 'excluir', 'remover', 'desenturmar')
PALAVRAS_INCLUIR = ('create', 'criar', 'novo', 'nova', 'cadastrar', 'enturmar', 'inscrever', 'lancar', 'chamada')

# Ação -> campo booleano correspondente em PermissaoGrupo
CAMPO_PERMISSAO = {
    'VISUALIZAR': 'visualizar',
    'INCLUIR': 'incluir',
    'ALTERAR': 'alterar',
    'EXCLUIR': 'excluir',
}


def ip_da_requisicao(request):
    encaminhado = request.META.get('HTTP_X_FORWARDED_FOR')
    if encaminhado:
        return encaminhado.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR') or None


def registrar_auditoria(request, acao, tela, funcionalidade, descricao, usuario=None, dados=None):
    """Cria um registro de auditoria (RF2002)."""
    from .models import RegistroAuditoria

    usuario = usuario or request.user
    if not usuario or not usuario.is_authenticated:
        return None
    return RegistroAuditoria.objects.create(
        usuario=usuario,
        acao=acao,
        tela=tela[:100],
        funcionalidade=funcionalidade[:100],
        descricao=descricao,
        ip_address=ip_da_requisicao(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        dados_alterados=dados,
    )


def classificar_acao(request, url_name):
    """Classifica a requisição como VISUALIZAR, INCLUIR, ALTERAR ou EXCLUIR."""
    if request.method in ('GET', 'HEAD', 'OPTIONS'):
        return 'VISUALIZAR'
    nome = (url_name or '').lower()
    if any(p in nome for p in PALAVRAS_EXCLUIR):
        return 'EXCLUIR'
    if any(p in nome for p in PALAVRAS_INCLUIR):
        return 'INCLUIR'
    return 'ALTERAR'


def bloqueio_aplicavel(modulo, acao, request=None):
    """Retorna o bloqueio ativo que impede a ação no módulo (ou None)."""
    from .models import BloqueioFuncionalidade

    if acao == 'VISUALIZAR':
        return None
    agora = timezone.now()
    bloqueios = BloqueioFuncionalidade.objects.filter(
        ativo=True,
        modulo=modulo,
        funcionalidade__in=[acao, 'TODOS'],
        data_inicio__lte=agora,
    ).filter(Q(data_fim__isnull=True) | Q(data_fim__gte=agora))

    tipo_ensino_enviado = request.POST.get('tipo_ensino') if request is not None else None
    for bloqueio in bloqueios:
        if bloqueio.tipo_bloqueio == 'DIRETO':
            return bloqueio
        if bloqueio.tipo_bloqueio == 'POR_ANO' and bloqueio.ano_administrativo == ano_atual():
            return bloqueio
        if bloqueio.tipo_bloqueio == 'POR_TIPO_ENSINO' and tipo_ensino_enviado and \
                bloqueio.tipo_ensino and bloqueio.tipo_ensino.upper() in tipo_ensino_enviado.upper():
            return bloqueio
    return None


def usuario_tem_permissao(user, modulo, acao):
    """
    Verifica as permissões dos grupos de acesso do usuário para o módulo.
    Se nenhum grupo do usuário tiver regras para o módulo, o acesso é liberado.
    """
    from .models import PermissaoGrupo

    if user.is_superuser:
        return True
    grupos = user.groups.values_list('name', flat=True)
    regras = PermissaoGrupo.objects.filter(
        grupo__nome__in=list(grupos), grupo__ativo=True, modulo=modulo,
        submenu__isnull=True, funcionalidade__isnull=True,
    )
    if not regras.exists():
        return True
    campo = CAMPO_PERMISSAO[acao]
    return regras.filter(**{campo: True}).exists()


class ControleAcessoMiddleware:
    """Aplica bloqueios de funcionalidade e permissões de grupo."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._auditar_alteracao(request, response)
        return response

    @staticmethod
    def _auditar_alteracao(request, response):
        """Registra na auditoria toda alteração bem-sucedida (POST seguido de redirecionamento)."""
        match = getattr(request, 'resolver_match', None)
        user = getattr(request, 'user', None)
        if (request.method != 'POST' or response.status_code != 302 or match is None
                or match.app_name in (None, '', 'admin') or user is None or not user.is_authenticated):
            return
        acao = {'INCLUIR': 'CREATE', 'EXCLUIR': 'DELETE'}.get(classificar_acao(request, match.url_name), 'UPDATE')
        registrar_auditoria(
            request, acao,
            tela=match.app_name,
            funcionalidade=match.url_name or '',
            descricao=f'{request.path}',
        )

    def process_view(self, request, view_func, view_args, view_kwargs):
        match = getattr(request, 'resolver_match', None)
        modulo = match.app_name if match else None
        user = getattr(request, 'user', None)
        if modulo in MODULOS_LIVRES or user is None or not user.is_authenticated or user.is_superuser:
            return None

        acao = classificar_acao(request, match.url_name)

        if not usuario_tem_permissao(user, modulo, acao):
            if acao == 'VISUALIZAR':
                return render(request, 'acesso_negado.html', {'modulo': modulo}, status=403)
            messages.error(request, 'Seu grupo de acesso não tem permissão para esta operação.')
            return redirect(request.META.get('HTTP_REFERER') or 'dashboard:home')

        bloqueio = bloqueio_aplicavel(modulo, acao, request)
        if bloqueio:
            messages.error(request, f'Operação bloqueada: {bloqueio.motivo}')
            return redirect(request.META.get('HTTP_REFERER') or 'dashboard:home')
        return None
