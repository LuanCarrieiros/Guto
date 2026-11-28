"""
Um diário por turma e disciplina.

- Remove diários duplicados da mesma turma/disciplina (mantendo o fechado ou o mais antigo).
- O período letivo passa a vir da turma e o professor da associação de professores,
  então os campos redundantes "periodo_letivo" e "professor" são removidos.
"""
from django.db import migrations


def remover_duplicados(apps, schema_editor):
    DiarioEletronico = apps.get_model('diario', 'DiarioEletronico')
    vistos = set()
    for diario in DiarioEletronico.objects.order_by('-diario_fechado', 'pk'):
        chave = (diario.turma_id, diario.disciplina_id)
        if chave in vistos:
            diario.delete()
        else:
            vistos.add(chave)


class Migration(migrations.Migration):

    dependencies = [
        ('diario', '0003_remove_modelos_sem_uso'),
        ('turma', '0012_mesclar_disciplinas_duplicadas'),
    ]

    operations = [
        migrations.RunPython(remover_duplicados, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(name='diarioeletronico', unique_together={('turma', 'disciplina')}),
        migrations.RemoveField(model_name='diarioeletronico', name='periodo_letivo'),
        migrations.RemoveField(model_name='diarioeletronico', name='professor'),
    ]
