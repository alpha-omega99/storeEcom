# Generated migration — ajout allows_personal_message et max_message_chars
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_alter_product_included_items'),  # Adapter selon votre dernière migration
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='allows_personal_message',
            field=models.BooleanField(
                default=False,
                help_text="Activer pour les packs premium (Écrin de Sérénité, Héritage Royal...)"
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='max_message_chars',
            field=models.PositiveSmallIntegerField(
                default=100,
                help_text="Nombre max de caractères pour le message personnalisé"
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='available_sizes',
            field=models.JSONField(
                default=list,
                blank=True,
                help_text="Ex: [\'60x90 cm\', \'70x110 cm\', \'80x120 cm\']"
            ),
        ),
    ]
