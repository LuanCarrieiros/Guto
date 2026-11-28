"""Remove modelos que nunca foram usados pelo sistema (tabelas vazias)."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("diario", "0002_diarioeletronico_data_fechamento_and_more"),
    ]

    operations = [
        migrations.DeleteModel(name="ConteudoAula"),
        migrations.DeleteModel(name="DiarioOnline"),
        migrations.DeleteModel(name="RegistroChamada"),
        migrations.DeleteModel(name="RegistroNota"),
    ]
