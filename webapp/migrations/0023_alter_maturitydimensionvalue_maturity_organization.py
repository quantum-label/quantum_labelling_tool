# Generated by Django 5.0.6 on 2024-11-05 12:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0022_remove_maturitydimensionvalue_maturity_matrix_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maturitydimensionvalue',
            name='maturity_organization',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.organization'),
        ),
    ]
