"""
Quem pode abrir cada diário.

- Administradores e usuários com acesso à área administrativa (coordenação/secretaria)
  veem todos os diários.
- Um usuário vinculado a um funcionário com função Docente vê apenas os diários das
  turmas/disciplinas em que tem associação vigente (Funcionários › Associação às Turmas).
  O professor regente (associação do tipo "Turma") vê todas as disciplinas da turma.
- Usuários sem vínculo com funcionário docente não são restringidos aqui (as regras de
  grupo de Utilitários continuam valendo).
"""
from django.core.exceptions import PermissionDenied

TODAS = '*'


def diarios_permitidos(user):
    """None = sem restrição; senão, {turma_id: {disciplina_id, ...} ou {'*'}}."""
    from funcionarios.models import AssociacaoProfessor, Funcionario

    if user.is_superuser or user.is_staff:
        return None
    funcionario = Funcionario.objects.filter(usuario=user).select_related('dados_funcionais').first()
    if funcionario is None or getattr(getattr(funcionario, 'dados_funcionais', None), 'funcao', None) != 'DOCENTE':
        return None
    permitidos = {}
    for assoc in AssociacaoProfessor.objects.vigentes().filter(funcionario=funcionario):
        permitidos.setdefault(assoc.turma_id, set()).add(assoc.disciplina_id or TODAS)
    return permitidos


def pode_acessar(user, turma, disciplina=None):
    permitidos = diarios_permitidos(user)
    if permitidos is None:
        return True
    disciplinas = permitidos.get(turma.pk)
    if disciplinas is None:
        return False
    return disciplina is None or TODAS in disciplinas or disciplina.pk in disciplinas


def exigir_acesso(user, turma, disciplina=None):
    if not pode_acessar(user, turma, disciplina):
        raise PermissionDenied('Você não é o professor desta turma/disciplina.')


def filtrar_turmas(user, turmas):
    permitidos = diarios_permitidos(user)
    return turmas if permitidos is None else turmas.filter(pk__in=permitidos.keys())


def filtrar_disciplinas(user, turma, disciplinas):
    permitidos = diarios_permitidos(user)
    if permitidos is None:
        return disciplinas
    ids = permitidos.get(turma.pk, set())
    return disciplinas if TODAS in ids else disciplinas.filter(pk__in=ids)
