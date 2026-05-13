from django.contrib import auth
from django.contrib.auth.models import User
from django.db import models


# Organization
class UserOrganization(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.organization.name} - {self.user.username}'


class Organization(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


# Maturity
class MaturityAssessment(models.Model):
    name = models.CharField(max_length=256)
    date = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE
    )
    rdf = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name} ({self.organization.name})'


# Maturity
class MaturityDimensionValue(models.Model):
    maturity_dimension_level = models.ForeignKey(
        'MaturityDimensionLevel',
        on_delete=models.CASCADE,
        default=None,
        null=True
    )
    maturity_dimension = models.ForeignKey(
        'MaturityDimension',
        on_delete=models.CASCADE,
        default=None
    )
    maturity_assessment = models.ForeignKey(
        'MaturityAssessment',
        on_delete=models.CASCADE,
        null=True,
        default=None
    )
    # TODO: To remove after migration
    maturity_organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        null=True,
        default=None
    )


class MaturityDimension(models.Model):
    name = models.CharField(max_length=256)
    definition = models.TextField()

    def __str__(self):
        return f'{self.name}'


class MaturityDimensionLevel(models.Model):
    value = models.IntegerField(default=0)
    text = models.TextField()

    maturity_dimension = models.ForeignKey(
        'MaturityDimension',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.maturity_dimension.name} - {self.value}. {self.text}'


# Dataset and Catalogue
class Catalogue(models.Model):
    title = models.CharField(max_length=256)
    version = models.FloatField()
    part_of = models.CharField(max_length=512)
    fdp_id = models.CharField(max_length=256, default=None, null=True, blank=True)

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )


class Dataset(models.Model):
    URI = models.CharField(max_length=512, blank=True, null=True)
    name = models.CharField(max_length=256)
    description = models.TextField()
    version = models.FloatField()
    rdf = models.TextField(blank=True, null=True)
    fdp_id = models.CharField(max_length=256, default=None, null=True, blank=True)

    dq_assessment = models.OneToOneField(
        'DQAssessment',
        on_delete=models.CASCADE,
        unique=True,
        blank=True,
        null=True
    )
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE
    )
    catalogue = models.ForeignKey(
        'Catalogue',
        on_delete=models.CASCADE,
        null=True  # TODO: To remove
    )
    maturity_assessment = models.ForeignKey(
        'MaturityAssessment',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


# Data Quality
class DQAssessment(models.Model):
    status = models.CharField(
        choices=models.TextChoices(
            'status',
            [
                ('O', 'Ongoing'),
                ('V', 'Validated')
            ]
        ),
        max_length=9,
        default='O'
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    rdf = models.TextField(blank=True, null=True)
    fdp_id = models.CharField(max_length=256, default=None, null=True, blank=True)


class EHDSCategory(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class DQDimension(models.Model):
    name = models.CharField(max_length=256)
    definition = models.TextField()
    relevance = models.FloatField(blank=True, null=True)

    ehds_category = models.ForeignKey(
        'EHDSCategory',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class DQMetric(models.Model):
    name = models.CharField(max_length=256)
    definition = models.TextField()
    additional_information = models.TextField(blank=True, null=True)
    measurement_approach = models.TextField(blank=True, null=True)
    formula = models.TextField(blank=True, null=True)
    weight = models.FloatField()
    needs_report_URL = models.BooleanField(default=False)

    dq_dimension = models.ForeignKey(
        'DQDimension',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.dq_dimension.name} - {self.name}'


class DQCategoricalMetric(DQMetric):
    pass


class DQCategoricalMetricCategory(models.Model):
    value = models.IntegerField(default=0)
    text = models.CharField(max_length=256, default='')

    dq_categorical_metric = models.ForeignKey(
        'DQCategoricalMetric',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.dq_categorical_metric.dq_dimension.name} - {self.dq_categorical_metric.name} - {self.value}. {self.text}'


class DQMetricValue(models.Model):
    value = models.CharField(max_length=256, blank=True, null=True)
    report_URL = models.TextField(blank=True, null=True, default=None)

    dq_metric = models.ForeignKey(
        'DQMetric',
        on_delete=models.CASCADE
    )
    dq_assessment = models.ForeignKey(
        'DQAssessment',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.dq_assessment.id} - {self.dq_metric.definition} - {self.value}'
