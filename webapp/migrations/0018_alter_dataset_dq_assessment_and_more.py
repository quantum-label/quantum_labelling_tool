# Generated by Django 5.0.6 on 2024-11-04 12:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0017_maturitydimension_remove_catalogue_fdp_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='dq_assessment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.dqassessment', unique=True),
        ),
        migrations.AlterField(
            model_name='maturitydimensionvalue',
            name='maturity_dimension',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.maturitydimensionlevel'),
        ),
    ]