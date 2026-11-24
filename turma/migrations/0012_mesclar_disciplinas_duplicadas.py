"""
Mescla disciplinas com o mesmo nome diferindo apenas em maiúsculas/minúsculas
(ex.: "MATEMÁTICA", "Matemática" e "matemática") e passa a impedir novas duplicatas.

A disciplina mantida é a mais usada (avaliações, aulas e diários); em empate,
a de nome com maiúsculas e minúsculas e, por fim, a mais antiga. Os registros que
apontavam para as duplicatas passam a apontar para ela.
"""
from django.db import IntegrityError, migrations, models, transaction
from django.db.models.functions import Lower


def mesclar(apps, schema_editor):
    Disciplina = apps.get_model('turma', 'Disciplina')
    relacionados = [
        rel for rel in Disciplina._meta.related_objects
        if rel.one_to_many or rel.one_to_one
    ]

    def uso(disciplina):
        return sum(rel.related_model.objects.filter(**{rel.field.name: disciplina}).count() for rel in relacionados)

    grupos = {}
    for disciplina in Disciplina.objects.order_by('pk'):
        grupos.setdefault(disciplina.nome.strip().lower(), []).append(disciplina)

    for duplicadas in grupos.values():
        if len(duplicadas) < 2:
            continue
        mantida = max(duplicadas, key=lambda d: (uso(d), d.nome not in (d.nome.upper(), d.nome.lower()), -d.pk))
        for disciplina in duplicadas:
            if disciplina.pk == mantida.pk:
                continue
            for rel in relacionados:
                for registro in rel.related_model.objects.filter(**{rel.field.name: disciplina}):
                    setattr(registro, rel.field.name, mantida)
                    try:
                        with transaction.atomic():
                            registro.save()
                    except IntegrityError:
                        # Já existe o mesmo registro para a disciplina mantida (ex.: diário da turma)
                        registro.delete()
            mantida.ativo = mantida.ativo or disciplina.ativo
            disciplina.delete()
        mantida.save()


class Migration(migrations.Migration):

    dependencies = [
        ('turma', '0011_enturmacao_historico'),
        ('diario', '0003_remove_modelos_sem_uso'),
    ]

    operations = [
        migrations.RunPython(mesclar, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='disciplina',
            constraint=models.UniqueConstraint(Lower('nome'), name='disciplina_nome_unico'),
        ),
    ]
