# Generated by Django 5.0.6 on 2024-09-06 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0004_alter_dataset_dq_assessment_alter_dataset_rdf_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dqassessment',
            name='start_date',
            field=models.DateTimeField(),
        ),
    ]