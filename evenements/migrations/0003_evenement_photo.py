# Generated by Django 5.1.6 on 2025-02-17 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evenements', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='evenement',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='evenements/'),
        ),
    ]
