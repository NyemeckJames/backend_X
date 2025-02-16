# Generated by Django 5.1.6 on 2025-02-16 10:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('billets', '0001_initial'),
        ('evenements', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='billet',
            name='evenement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billets', to='evenements.evenement'),
        ),
        migrations.AddField(
            model_name='billet',
            name='participant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billets', to=settings.AUTH_USER_MODEL),
        ),
    ]
