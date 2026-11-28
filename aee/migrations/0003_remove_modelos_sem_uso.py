"""Remove modelos que nunca foram usados pelo sistema (tabelas vazias)."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("aee", "0002_alter_projetopedagogico_periodo_letivo_and_more"),
    ]

    operations = [
        migrations.DeleteModel(name="AssociacaoEscola"),
    ]
