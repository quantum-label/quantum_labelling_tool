# Generated by Django 5.1 on 2024-09-20 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0012_dqdimension_relevance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dqdimension',
            name='relevance',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
