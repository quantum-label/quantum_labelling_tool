# Generated by Django 5.1 on 2025-01-28 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0025_alter_dataset_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='dqmetric',
            name='needs_report_URL',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='dqmetricvalue',
            name='report_URL',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
