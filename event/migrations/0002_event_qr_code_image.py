# Generated by Django 5.1.6 on 2025-02-27 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='qr_code_image',
            field=models.ImageField(blank=True, null=True, upload_to='events/qrcodes/'),
        ),
    ]
