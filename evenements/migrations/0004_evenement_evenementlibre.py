# Generated by Django 5.1.6 on 2025-02-17 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evenements', '0003_evenement_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='evenement',
            name='evenementLibre',
            field=models.BooleanField(default=False),
        ),
    ]
