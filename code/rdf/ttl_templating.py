import os

from code.helpers.django import generate_assessment_stars, compute_amount_of_stars
from code.label.label import compute_scores
from webapp.models import Dataset, Catalogue, DQMetricValue, DQMetric, DQDimension, EHDSCategory, DQAssessment


def format_name(dimension_name: str) -> str:
    """
    Converts a dimension name into a format suitable for RDF.
    - If the name has one word (e.g., "accuracy"), it remains unchanged.
    - If the name has multiple words (e.g., "data provenance"), it is converted to "DataProvenance".

    :param dimension_name: The original dimension name.
    :return: A formatted string with no spaces and capitalized initials.
    """
    words = dimension_name.split()
    return '_'.join(word.capitalize() for word in words)

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


#def template_dataset(catalogue: Catalogue, dataset: Dataset) -> str:
#    return f'''
#<{os.getenv('FDP_URL', '')}/dataset/{dataset.fdp_id or dataset.name}> 
#    a dcat:Dataset ;
#    dcterms:title "{dataset.name}" ;
#    dct:hasVersion "{dataset.version}" ;
#    dct:description "{dataset.description}" ;
#    dct:isPartOf <http://{os.getenv('FDP_URL', None)}/catalog/{catalogue.fdp_id or catalogue.title}>;
#    dqv:hasQualityAnnotation <{os.getenv('FDP_URL', None)}/qualityCertificate/{dataset.fdp_id or ''}> 
#    .
#'''


# def template_distribution(dataset: Dataset) -> str:
#     return f'''> a dcat:Distribution ;
#             dcat:downloadURL <http://www.example.org/files/mydataset.csv> ;
#             dcterms:title "CSV distribution of dataset" ;
#             dcat:mediaType "text/csv" ;
#             dcat:byteSize "NA"^^xsd:decimal .'''


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
    #dataset_filled_template = template_dataset(
    #    catalogue=catalogue,
    #    dataset=dataset
    #)
    # distribution_filled_template = template_distribution(dataset=dataset)

    final_ttl += prefix + '\n'
    final_ttl += catalogue_filled_template + '\n'
    #final_ttl += dataset_filled_template + '\n'
    #final_ttl += distribution_filled_template + '\n'

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

    final_ttl += temporal_ttl

    return final_ttl
