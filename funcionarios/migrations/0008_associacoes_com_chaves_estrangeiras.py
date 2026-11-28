"""
Associações de professores e profissionais passam a apontar para a turma e a
disciplina cadastradas (chaves estrangeiras) em vez de guardar o nome como texto.
Com o nome, turmas homônimas (ex.: "1º A" de anos diferentes) se confundiam.

Registros antigos são convertidos pelo nome; se houver turmas homônimas, usa-se a
do período letivo mais recente. Registros sem correspondência são descartados
(a tabela estava vazia na base de demonstração).
Também adiciona o vínculo opcional entre funcionário e usuário de acesso.
"""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def normalizar(texto):
    return ' '.join((texto or '').split()).casefold()


def converter(apps, schema_editor):
    Turma = apps.get_model('turma', 'Turma')
    Disciplina = apps.get_model('turma', 'Disciplina')
    AssociacaoProfessor = apps.get_model('funcionarios', 'AssociacaoProfessor')
    AssociacaoOutros = apps.get_model('funcionarios', 'AssociacaoOutrosProfissionais')
    DisciplinaFuncionario = apps.get_model('funcionarios', 'DisciplinaFuncionario')

    # Nome exato tem prioridade; depois, ignorando maiúsculas/espaços. Em homônimas, vale o ano mais recente.
    exatas, aproximadas = {}, {}
    for turma in Turma.objects.order_by('periodo_letivo', 'pk'):
        exatas[turma.nome.strip()] = turma
        aproximadas[normalizar(turma.nome)] = turma
    disciplinas = {normalizar(d.nome): d for d in Disciplina.objects.all()}

    class Turmas:
        @staticmethod
        def get(nome):
            return exatas.get((nome or '').strip()) or aproximadas.get(normalizar(nome))

    turmas = Turmas()

    for assoc in AssociacaoProfessor.objects.all():
        turma = turmas.get(assoc.turma_nome)
        if turma is None:
            assoc.delete()
            continue
        assoc.turma_ref = turma
        assoc.disciplina_ref = disciplinas.get(normalizar(assoc.disciplina_nome))
        if assoc.tipo_associacao not in ('DISCIPLINA', 'TURMA'):
            assoc.tipo_associacao = 'DISCIPLINA'
        assoc.save()

    for assoc in AssociacaoOutros.objects.all():
        turma = turmas.get(assoc.turma_nome)
        if turma is None:
            assoc.delete()
        else:
            assoc.turma_ref = turma
            assoc.save()

    vistos = set()
    for item in DisciplinaFuncionario.objects.order_by('pk'):
        disciplina = disciplinas.get(normalizar(item.disciplina_nome))
        chave = (item.funcionario_id, disciplina.pk if disciplina else None)
        if disciplina is None or chave in vistos:
            item.delete()
        else:
            vistos.add(chave)
            item.disciplina_ref = disciplina
            item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('funcionarios', '0007_alter_funcionario_sexo'),
        ('turma', '0012_mesclar_disciplinas_duplicadas'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1) Guarda os nomes antigos e cria as novas referências (temporariamente opcionais)
        migrations.AlterUniqueTogether(name='associacaoprofessor', unique_together=set()),
        migrations.RenameField('associacaoprofessor', 'turma', 'turma_nome'),
        migrations.RenameField('associacaoprofessor', 'disciplina', 'disciplina_nome'),
        migrations.RenameField('associacaooutrosprofissionais', 'turma', 'turma_nome'),
        migrations.RenameField('disciplinafuncionario', 'disciplina', 'disciplina_nome'),
        migrations.AddField(
            model_name='associacaoprofessor', name='turma_ref',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='turma.turma'),
        ),
        migrations.AddField(
            model_name='associacaoprofessor', name='disciplina_ref',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='turma.disciplina'),
        ),
        migrations.AddField(
            model_name='associacaooutrosprofissionais', name='turma_ref',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='turma.turma'),
        ),
        migrations.AddField(
            model_name='disciplinafuncionario', name='disciplina_ref',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='turma.disciplina'),
        ),
        # 2) Converte os nomes em referências
        migrations.RunPython(converter, migrations.RunPython.noop),
        # 3) Remove os campos de texto e assume os nomes definitivos
        migrations.RemoveField('associacaoprofessor', 'turma_nome'),
        migrations.RemoveField('associacaoprofessor', 'disciplina_nome'),
        migrations.RemoveField('associacaooutrosprofissionais', 'turma_nome'),
        migrations.RemoveField('disciplinafuncionario', 'disciplina_nome'),
        migrations.RenameField('associacaoprofessor', 'turma_ref', 'turma'),
        migrations.RenameField('associacaoprofessor', 'disciplina_ref', 'disciplina'),
        migrations.RenameField('associacaooutrosprofissionais', 'turma_ref', 'turma'),
        migrations.RenameField('disciplinafuncionario', 'disciplina_ref', 'disciplina'),
    ]
