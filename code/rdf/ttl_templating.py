import os
import re

from code.helpers.django import generate_assessment_stars, compute_amount_of_stars
from code.label.label import compute_scores, compute_maturity_score
from webapp.models import Dataset, Catalogue, DQMetricValue, DQMetric, DQDimension, EHDSCategory, DQAssessment, \
    MaturityAssessment, MaturityDimensionValue, MaturityDimension


def escape_quotes(text: str) -> str:
    if text is None:
        return ""
    return text.replace('"', '\\"')


def format_name(dimension_name: str) -> str:
    """
    Converts a dimension name into a format suitable for RDF.
    - Removes special characters.
    - Joins words with underscores.

    :param dimension_name: The original dimension name.
    :return: A formatted string.
    """
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', dimension_name)
    return '_'.join(clean_name.split())


def template_prefix() -> str:
    return f'''@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix dqv: <http://www.w3.org/TR/vocab-dqv/#> .
@prefix qnt: <http://quantumproject.eu/vocab-quantum/#> .
@prefix oa: <http://www.w3.org/ns/oa#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
'''


def template_catalogue(catalogue: Catalogue) -> str:
    return f'''
<{os.getenv('FDP_URL', '')}/catalog/{catalogue.fdp_id or catalogue.id}> 
    a dcat:Catalog ;
    dct:title "{catalogue.title}" ;
    dct:hasVersion "{catalogue.version}" ;
    dct:isPartOf <{os.getenv('FDP_URL', '')}> .
'''


# def template_dataset(catalogue: Catalogue, dataset: Dataset) -> str:
#    return f'''
# <{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.name}>
#    a dcat:Dataset ;
#    dcterms:title "{dataset.name}" ;
#    dct:hasVersion "{dataset.version}" ;
#    dct:description "{dataset.description}" ;
#    dct:isPartOf <http://{os.getenv('FDP_URL', None)}/catalog/{catalogue.fdp_id or catalogue.title}>;
#    dqv:hasQualityAnnotation <{os.getenv('FDP_URL', None)}/qualityCertificate/{dataset.fdp_id or ''}> 
#    .
# '''


def template_quality_certificate(
        catalogue: Catalogue,
        dataset: Dataset,
        dimensions: list,
        measurement_names: list,
        dq_assesment: DQAssessment,
        stars_text: str
) -> str:
    dimensions_str = ",\n    ".join(f"qnt:{dimension}" for dimension in dimensions)
    measurements_str = ",\n    ".join(f"qnt:{measurement_name}" for measurement_name in measurement_names)

    ttl = f'''
<{os.getenv('FDP_URL', '')}/qualityCertificate/{dq_assesment.fdp_id or dq_assesment.id}> 
    a dqv:QualityCertificate ;
    oa:hasTarget <{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.id}> ;
    dct:isPartOf <{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.id}> ;
    oa:hasBody qnt:{stars_text} ;
    dct:title "Quality label"@en ;    
    oa:motivatedBy dqv:qualityAssessment ;
    dqv:inDimension 
    {dimensions_str} .  
    
qnt:CustomQuantumQuality
    a skos:ConceptScheme ;
    skos:prefLabel "Quantum Data Quality"@en ;
    skos:definition "Rating System for Evaluating Dataset Data Quality within the QUANTUM Framework"@en 
    .
    
qnt:zero_stars
    a skos:Concept ;
    skos:inScheme qnt:CustomQuantumQuality ;
    skos:prefLabel "Zero star"@en ;
    skos:definition "Zero star corresponds to a median data quality score in the range 0%-24%"@en 
    .
    
qnt:one_star
    a skos:Concept ;
    skos:inScheme qnt:CustomQuantumQuality ;
    skos:prefLabel "One star"@en ;
    skos:definition "One star corresponds to a median data quality score in the range 25%-44%"@en 
    .

qnt:two_stars
    a skos:Concept ;
    skos:inScheme qnt:CustomQuantumQuality ;
    skos:prefLabel "Two stars"@en ;
    skos:definition "Two stars correspond to a median data quality score in the range 45%-59%"@en 
    .

qnt:three_stars
    a skos:Concept ;
    skos:inScheme qnt:CustomQuantumQuality ;
    skos:prefLabel "Three stars"@en ;
    skos:definition "Three stars correspond to a median data quality score in the range 60%-79%"@en 
    .

qnt:four_stars
    a skos:Concept ;
    skos:inScheme qnt:CustomQuantumQuality ;
    skos:prefLabel "Four stars"@en ;
    skos:definition "Four stars correspond to a median data quality score in the range 80%-89%"@en 
    .

qnt:five_stars
    a skos:Concept ;
    skos:inScheme qnt:CustomQuantumQuality ;
    skos:prefLabel "Five stars"@en ;
    skos:definition "Five stars correspond to a median data quality score in the range 90%-100%"@en 
    .
    
<{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.id}>
    a dcat:Dataset ;
    dcterms:title "{dataset.name}" ;
    dct:hasVersion "{dataset.version}" ;
    dct:description "{dataset.description}" ;
    dct:isPartOf <http://{os.getenv('FDP_URL', '')}/catalog/{catalogue.fdp_id or catalogue.id}> ;
    dqv:hasQualityAnnotation <{os.getenv('FDP_URL', '')}/qualityCertificate/{dataset.fdp_id or dq_assesment.id}> ;
    dqv:hasQualityMeasurement
    {measurements_str} .
    '''
    return ttl


def template_categorical_metric_value(
        metric_value: DQMetricValue,
        metric_name: str,
        measurement_name: str,
        dataset: Dataset
) -> str:
    return f'''
qnt:{measurement_name} 
    a dqv:QualityMeasurement ;
    dqv:computedOn <{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.id}> ;
    dqv:isMeasurementOf qnt:{metric_name} ;
    dqv:value "{metric_value.value}"^^xsd:integer ;
    .
'''


def template_metric(metric: DQMetric, metric_name: str) -> str:
    return f'''
qnt:{metric_name}
    a dqv:Metric ;
    skos:definition "{metric.definition}"@en ;
    dqv:expectedDataType xsd:integer ;
    dqv:inDimension qnt:{format_name(metric.dq_dimension.name)} ;
    .
'''


def template_dimension(dimension: DQDimension) -> str:
    return f'''
qnt:{format_name(dimension.name)}
    a dqv:Dimension ;
    skos:prefLabel "{dimension.name}"@en ;
    skos:definition "{dimension.definition}"@en ;
    dqv:inCategory qnt:{format_name(dimension.ehds_category.name)} ;
    .
'''


def template_ehds_category(category: EHDSCategory) -> str:
    return f'''
qnt:{format_name(category.name)}
    a dqv:Category ;
    skos:prefLabel "{category.name}"@en ;
    skos:definition "category_definition";
    .
'''


def template_maturity_assessment(
        dataset: Dataset,
        assessment: MaturityAssessment,
        score: int,
        dimension_names: list,
        measurement_names: list
) -> str:
    dimensions_str = ",\n    ".join(f"qnt:{dimension}" for dimension in dimension_names)
    measurements_str = ",\n    ".join(f"qnt:{measurement_name}" for measurement_name in measurement_names)

    return f'''
<{os.getenv('FDP_URL', '')}/maturity/{assessment.id}>
    a qnt:MaturityAssessment ;
    oa:hasTarget <{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.id}> ;
    dct:title "{escape_quotes(assessment.name)}"@en ;
    qnt:maturityScore "{score}"^^xsd:integer ;
    dqv:inDimension 
    {dimensions_str} ;
    qnt:hasMaturityMeasurement
    {measurements_str} .
'''


def template_maturity_measurement(
        assessment: MaturityAssessment,
        dimension_name: str,
        value: int,
        dataset: Dataset
) -> str:
    return f'''
qnt:{format_name(dimension_name)}_maturity_measurement 
    a qnt:MaturityMeasurement ;
    qnt:computedOn <{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.id}> ;
    qnt:isMeasurementOf qnt:{format_name(dimension_name)}_maturity_dimension ;
    dqv:value "{value}"^^xsd:integer ;
    .
'''


def template_maturity_dimension(dimension: MaturityDimension) -> str:
    return f'''
qnt:{format_name(dimension.name)}_maturity_dimension
    a qnt:MaturityDimension ;
    skos:prefLabel "{dimension.name}"@en ;
    skos:definition "{escape_quotes(dimension.definition)}"@en ;
    .
'''


def generate_ttl_file(
        catalogue: Catalogue,
        dataset: Dataset,
        username: str
) -> str:
    final_ttl = ''

    prefix = template_prefix()
    catalogue_filled_template = template_catalogue(
        catalogue=catalogue,
    )
    # dataset_filled_template = template_dataset(
    #    catalogue=catalogue,
    #    dataset=dataset
    # )

    final_ttl += prefix + '\n'
    final_ttl += catalogue_filled_template + '\n'
    # final_ttl += dataset_filled_template + '\n'

    assessment = dataset.dq_assessment

    ehds_categories = EHDSCategory.objects.all()

    temporal_ttl = ''
    dimension_names = []
    measurement_names = []

    _, score = compute_scores(dataset)
    score = int(score)
    stars = compute_amount_of_stars(score)
    stars_text = 'zero_stars'

    if stars == 1:
        stars_text = 'one_star'
    elif stars == 2:
        stars_text = 'two_stars'
    elif stars == 3:
        stars_text = 'three_stars'
    elif stars == 4:
        stars_text = 'four_stars'
    elif stars >= 5:
        stars_text = 'five_stars'

    # We fill the dictionary with all the information to build the web page
    for category in ehds_categories:
        category_filled_template = template_ehds_category(category=category)

        dimensions = DQDimension.objects.filter(ehds_category=category)
        for dimension in dimensions:
            dimension_filled_template = template_dimension(dimension=dimension)
            dimension_names.append(format_name(dimension.name))

            metrics = DQMetric.objects.filter(dq_dimension=dimension)
            for index, metric in enumerate(metrics):
                metric_name = f'{format_name(dimension.name)}_metric{index + 1}'
                measurement_name = f'{format_name(dimension.name)}_measurement{index + 1}'
                measurement_names.append(measurement_name)
                metric_filled_template = template_metric(metric=metric, metric_name=metric_name)

                dq_metric_value = DQMetricValue.objects.filter(dq_assessment=assessment, dq_metric=metric)
                current_value = None

                # If the metric is filled then we assign the value, else it is None
                if len(dq_metric_value) >= 1:
                    dq_metric_value = dq_metric_value.first()
                    # For the categorical metrics we provide the possible values
                    if getattr(metric, 'dqcategoricalmetric') is not None:
                        metric_value_filled_template = template_categorical_metric_value(
                            metric_value=dq_metric_value,
                            metric_name=metric_name,
                            measurement_name=measurement_name,
                            dataset=dataset
                        )

                        temporal_ttl += metric_value_filled_template + '\n'

                temporal_ttl += metric_filled_template + '\n'

            temporal_ttl += dimension_filled_template + '\n'

        temporal_ttl += category_filled_template + '\n'

    final_ttl += template_quality_certificate(
        catalogue,
        dataset,
        dimension_names,
        measurement_names,
        assessment,
        stars_text
    ) + '\n'

    # Add Maturity Assessment if linked
    if dataset.maturity_assessment:
        maturity_assessment = dataset.maturity_assessment
        _, total_maturity_score = compute_maturity_score(assessment=maturity_assessment)

        maturity_dimension_names = []
        maturity_measurement_names = []
        maturity_temporal_ttl = ''

        maturity_dimensions = MaturityDimension.objects.all()
        for dimension in maturity_dimensions:
            maturity_dimension_value = MaturityDimensionValue.objects.filter(
                maturity_dimension=dimension,
                maturity_assessment=maturity_assessment
            ).first()

            if maturity_dimension_value is not None:
                maturity_temporal_ttl += template_maturity_dimension(dimension) + '\n'
                maturity_dimension_names.append(f"{format_name(dimension.name)}_maturity_dimension")

                m_name = f"{format_name(dimension.name)}_maturity_measurement"
                maturity_measurement_names.append(m_name)
                maturity_temporal_ttl += template_maturity_measurement(
                    maturity_assessment,
                    dimension.name,
                    maturity_dimension_value.maturity_dimension_level.value,
                    dataset
                ) + '\n'

        final_ttl += template_maturity_assessment(
            dataset,
            maturity_assessment,
            total_maturity_score,
            maturity_dimension_names,
            maturity_measurement_names
        ) + '\n'
        final_ttl += maturity_temporal_ttl

        # Standalone relation from dataset to maturity assessment
        final_ttl += f'''<{os.getenv("FDP_URL", "")}/dataset/{dataset.fdp_id or dataset.id}> qnt:hasMaturityAssessment <{os.getenv('FDP_URL', '')}/maturity/{maturity_assessment.id}> .\n'''

    final_ttl += temporal_ttl

    return final_ttl
