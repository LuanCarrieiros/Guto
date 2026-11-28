"""Remove modelos que nunca foram usados pelo sistema (tabelas vazias)."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("utilitarios", "0003_remove_tipoavaliacao_duplicado"),
    ]

    operations = [
        migrations.DeleteModel(name="AssociacaoUsuarioInstituicao"),
        migrations.DeleteModel(name="CabecalhoRelatorio"),
        migrations.DeleteModel(name="MatriculaRapida"),
    ]
