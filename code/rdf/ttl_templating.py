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
@prefix dqv: <http://www.w3.org/ns/dqv#> .
@prefix qnt: <http://quantumproject.eu/vocab-quantum/#> .
@prefix oa: <http://www.w3.org/ns/oa#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix org: <http://www.w3.org/ns/org#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
'''


def template_quantum_vocabulary() -> str:
    return '''
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

qnt:MaturityDimension
    a rdfs:Class ;
    rdfs:subClassOf dqv:Dimension ;
    rdfs:label "Maturity dimension"@en ;
    rdfs:comment "A dimension used to assess the maturity of an organisation, process, or governance structure related to a dataset."@en .

qnt:MaturityMeasurement
    a rdfs:Class ;
    rdfs:subClassOf dqv:QualityMeasurement ;
    rdfs:label "Maturity measurement"@en ;
    rdfs:comment "A measurement used to assess the maturity level of an organisation, process, or governance structure related to a dataset."@en .
'''


def template_catalogue(catalogue: Catalogue, dataset: Dataset) -> str:
    return f'''
<{os.getenv('FDP_URL', '')}/catalog/{catalogue.fdp_id or catalogue.id}> 
    a dcat:Catalog ;
    dct:title "{catalogue.title}" ;
    dct:hasVersion "{catalogue.version}" ;
    dcat:dataset <{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.id}> .
'''


def template_dataset(
        catalogue: Catalogue,
        dataset: Dataset,
        dq_assessment: DQAssessment,
        measurement_names: list,
        has_maturity: bool,
        workflow_id: str
) -> str:
    measurements_str = ",\n    ".join(f"qnt:{measurement_name}" for measurement_name in measurement_names)
    ttl = f'''
<{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.id}>
    a dcat:Dataset ;
    dcterms:title "{dataset.name}" ;
    dct:hasVersion "{dataset.version}" ;
    dct:description "{dataset.description}" ;
    dct:isPartOf <{os.getenv('FDP_URL', '')}/catalog/{catalogue.fdp_id or catalogue.id}> ;
    dqv:hasQualityAnnotation <{os.getenv('FDP_URL', '')}/qualityCertificate/{dataset.fdp_id or dq_assessment.id}> ;
    dqv:hasQualityMeasurement
    {measurements_str} '''

    if has_maturity:
        ttl += f''';
    qnt:governedBy qnt:{workflow_id} .
'''
    else:
        ttl += f''' .
'''
    return ttl


def template_organization_and_workflow(organization, workflow_id: str, assessment_id: str) -> str:
    org_id = format_name(organization.name)
    return f'''
qnt:{org_id}
    a org:Organization ;
    rdfs:label "{escape_quotes(organization.name)}"@en ;
    org:hasUnit qnt:{workflow_id} .

qnt:{workflow_id}
    a qnt:GovernanceWorkflow ;
    rdfs:label "{escape_quotes(organization.name)} Governance Workflow"@en ;
    org:unitOf qnt:{org_id} ;
    qnt:hasMaturityAssessment <{os.getenv('FDP_URL', '')}/maturity/{assessment_id}> .
'''


def template_quality_certificate(
        dataset: Dataset,
        dimensions: list,
        dq_assessment: DQAssessment,
        stars_text: str,
        has_maturity: bool,
        maturity_assessment: MaturityAssessment = None
) -> str:
    dimensions_str = ",\n    ".join(f"qnt:{dimension}" for dimension in dimensions)

    ttl = f'''
<{os.getenv('FDP_URL', '')}/qualityCertificate/{dq_assessment.fdp_id or dq_assessment.id}> 
    a dqv:QualityCertificate ;
    oa:hasTarget <{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.id}> ;
    dct:isPartOf <{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.id}> ;
    oa:hasBody qnt:{stars_text} ;
    dct:title "Quality label"@en ;    
    oa:motivatedBy dqv:qualityAssessment ;
    dqv:inDimension 
    {dimensions_str} '''
    
    if has_maturity and maturity_assessment:
        ttl += f''';
    qnt:associatedMaturityAssessment <{os.getenv('FDP_URL', '')}/maturity/{maturity_assessment.id}> .
'''
    else:
        ttl += f''' .
'''
    return ttl


def template_ehds_category(category: EHDSCategory) -> str:
    return f'''
qnt:{format_name(category.name)}
    a dqv:Category ;
    skos:prefLabel "{category.name}"@en ;
    skos:definition "category_definition";
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


def template_metric(metric: DQMetric, metric_name: str) -> str:
    return f'''
qnt:{metric_name}
    a dqv:Metric ;
    skos:definition "{metric.definition}"@en ;
    dqv:expectedDataType xsd:integer ;
    dqv:inDimension qnt:{format_name(metric.dq_dimension.name)} ;
    .
'''


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


def template_maturity_assessment(
        assessment: MaturityAssessment,
        score: int,
        dimension_names: list,
        measurement_names: list,
        workflow_id: str
) -> str:
    dimensions_str = ",\n    ".join(f"qnt:{dimension}" for dimension in dimension_names)
    measurements_str = ",\n    ".join(f"qnt:{measurement_name}" for measurement_name in measurement_names)

    return f'''
<{os.getenv('FDP_URL', '')}/maturity/{assessment.id}>
    a qnt:MaturityAssessment ;
    oa:hasTarget qnt:{workflow_id} ;
    dct:title "{escape_quotes(assessment.name)}"@en ;
    qnt:maturityScore "{score}"^^xsd:integer ;
    dqv:inDimension 
    {dimensions_str} ;
    qnt:hasMaturityMeasurement
    {measurements_str} .
'''


def template_maturity_dimension(dimension: MaturityDimension) -> str:
    return f'''
qnt:{format_name(dimension.name)}_maturity_dimension
    a qnt:MaturityDimension ;
    skos:prefLabel "{dimension.name}"@en ;
    skos:definition "{escape_quotes(dimension.definition)}"@en ;
    .
'''


def template_maturity_metric(dimension_name: str) -> str:
    clean_name = format_name(dimension_name).replace('_', ' ').lower()
    return f'''
qnt:{format_name(dimension_name)}_maturity_metric
    a dqv:Metric ;
    skos:definition "Maturity level of {clean_name}."@en ;
    dqv:expectedDataType xsd:integer ;
    dqv:inDimension qnt:{format_name(dimension_name)}_maturity_dimension .
'''


def template_maturity_measurement(
        assessment: MaturityAssessment,
        dimension_name: str,
        value: int,
        dataset: Dataset,
        workflow_id: str
) -> str:
    return f'''
qnt:{format_name(dimension_name)}_maturity_measurement 
    a qnt:MaturityMeasurement ;
    dqv:computedOn qnt:{workflow_id} ;
    dqv:value "{value}"^^xsd:integer ;
    dqv:inDimension qnt:{format_name(dimension_name)}_maturity_dimension .
'''


def generate_ttl_file(
        catalogue: Catalogue,
        dataset: Dataset,
        username: str
) -> str:
    final_ttl = ''

    # 1. Prefixes
    final_ttl += template_prefix() + '\n'

    # 2. QUANTUM vocabulary/specification block
    final_ttl += template_quantum_vocabulary() + '\n'

    # Retrieve common data
    assessment = dataset.dq_assessment
    ehds_categories = EHDSCategory.objects.all()

    dimension_names = []
    measurement_names = []
    qu_categories_ttl = ''
    qu_dimensions_ttl = ''
    qu_metrics_ttl = ''
    qu_measurements_ttl = ''

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

    # Evaluate Q&U Assessment objects
    for category in ehds_categories:
        qu_categories_ttl += template_ehds_category(category=category) + '\n'

        dimensions = DQDimension.objects.filter(ehds_category=category)
        for dimension in dimensions:
            qu_dimensions_ttl += template_dimension(dimension=dimension) + '\n'
            dimension_names.append(format_name(dimension.name))

            metrics = DQMetric.objects.filter(dq_dimension=dimension)
            for index, metric in enumerate(metrics):
                metric_name = f'{format_name(dimension.name)}_metric{index + 1}'
                measurement_name = f'{format_name(dimension.name)}_measurement{index + 1}'
                measurement_names.append(measurement_name)
                qu_metrics_ttl += template_metric(metric=metric, metric_name=metric_name) + '\n'

                dq_metric_value = DQMetricValue.objects.filter(dq_assessment=assessment, dq_metric=metric)

                if len(dq_metric_value) >= 1:
                    dq_metric_value = dq_metric_value.first()
                    has_categorical = False
                    try:
                        has_categorical = getattr(metric, 'dqcategoricalmetric', None) is not None
                    except Exception:
                        pass
                        
                    if has_categorical:
                        qu_measurements_ttl += template_categorical_metric_value(
                            metric_value=dq_metric_value,
                            metric_name=metric_name,
                            measurement_name=measurement_name,
                            dataset=dataset
                        ) + '\n'

    has_maturity = dataset.maturity_assessment is not None
    maturity_assessment = dataset.maturity_assessment

    workflow_id = ''
    if has_maturity:
        workflow_id = f"{format_name(dataset.organization.name)}_GovernanceWorkflow"

    # 3. Core DCAT metadata
    final_ttl += template_catalogue(catalogue=catalogue, dataset=dataset) + '\n'
    final_ttl += template_dataset(
        catalogue=catalogue,
        dataset=dataset,
        dq_assessment=assessment,
        measurement_names=measurement_names,
        has_maturity=has_maturity,
        workflow_id=workflow_id
    ) + '\n'

    if has_maturity:
        final_ttl += template_organization_and_workflow(dataset.organization, workflow_id, maturity_assessment.id) + '\n'

    # 4. Quality and Utility assessment block
    final_ttl += template_quality_certificate(
        dataset=dataset,
        dimensions=dimension_names,
        dq_assessment=assessment,
        stars_text=stars_text,
        has_maturity=has_maturity,
        maturity_assessment=maturity_assessment
    ) + '\n'
    final_ttl += qu_categories_ttl
    final_ttl += qu_dimensions_ttl
    final_ttl += qu_metrics_ttl
    final_ttl += qu_measurements_ttl

    # 5. Maturity assessment block
    if has_maturity:
        _, total_maturity_score = compute_maturity_score(assessment=maturity_assessment)

        maturity_dimension_names = []
        maturity_measurement_names = []
        
        maturity_dimensions_ttl = ''
        maturity_metrics_ttl = ''
        maturity_measurements_ttl = ''

        maturity_dimensions = MaturityDimension.objects.all()
        for dimension in maturity_dimensions:
            maturity_dimension_value = MaturityDimensionValue.objects.filter(
                maturity_dimension=dimension,
                maturity_assessment=maturity_assessment
            ).first()

            if maturity_dimension_value is not None:
                maturity_dimensions_ttl += template_maturity_dimension(dimension) + '\n'
                maturity_dimension_names.append(f"{format_name(dimension.name)}_maturity_dimension")

                maturity_metrics_ttl += template_maturity_metric(dimension.name) + '\n'

                m_name = f"{format_name(dimension.name)}_maturity_measurement"
                maturity_measurement_names.append(m_name)
                maturity_measurements_ttl += template_maturity_measurement(
                    maturity_assessment,
                    dimension.name,
                    maturity_dimension_value.maturity_dimension_level.value,
                    dataset,
                    workflow_id
                ) + '\n'

        final_ttl += template_maturity_assessment(
            assessment=maturity_assessment,
            score=total_maturity_score,
            dimension_names=maturity_dimension_names,
            measurement_names=maturity_measurement_names,
            workflow_id=workflow_id
        ) + '\n'
        final_ttl += maturity_dimensions_ttl
        final_ttl += maturity_metrics_ttl
        final_ttl += maturity_measurements_ttl

    return final_ttl
