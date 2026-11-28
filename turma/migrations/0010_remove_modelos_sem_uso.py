"""Remove modelos que nunca foram usados pelo sistema (tabelas vazias)."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("turma", "0009_alter_turma_periodo_letivo"),
    ]

    operations = [
        migrations.DeleteModel(name="ParecerDescritivo"),
        migrations.DeleteModel(name="HabilidadeCompetencia"),
        migrations.DeleteModel(name="MediaGlobalConceito"),
        migrations.DeleteModel(name="AtestadoMedico"),
        migrations.DeleteModel(name="GrupoConceito"),
        migrations.DeleteModel(name="LancamentoNota"),
        migrations.DeleteModel(name="PendenciaAvaliacao"),
    ]
