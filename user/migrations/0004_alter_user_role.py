# Generated by Django 5.1.6 on 2025-02-27 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_user_prenom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('ADMINISTRATEUR', 'Admin'), ('ORGANISATEUR', 'Organisateur'), ('PARTICIPANT', 'Participant')], default='PARTICIPANT', max_length=20),
        ),
    ]
