import os
from datetime import datetime

from django.db.models import Sum

from code.helpers.django import generate_assessment_stars
from code.label.label import plot_label, compute_scores
from code.label.pdf.pdf_creator import PDFCreator
from webapp.models import Dataset, Catalogue, DQAssessment, Organization, DQMetric, DQDimension, EHDSCategory, DQMetricValue, DQCategoricalMetricCategory


class DQAssessmentPDFCreator(PDFCreator):
    def __init__(self, dataset: Dataset, catalogue: Catalogue, assessment: DQAssessment, organization: Organization):
        super().__init__()

        self.organization = organization
        self.assessment = assessment
        self.catalogue = catalogue
        self.dataset = dataset

    def _get_templates_path(self):
        return os.path.dirname(os.path.abspath(__file__)) + '/templates'

    def _generate_data(self):
        """
        Generate the data for a dq assessment
        @return:
        """
        _, score = compute_scores(self.dataset)
        score = int(score)

        results = self.__generate_results()

        data = {
            'stars': generate_assessment_stars(score),
            'label': plot_label(self.dataset, output_type='img'),
            'score': score,
            'dataset': self.dataset,
            'catalogue': self.catalogue,
            'organization': self.organization,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '0.1',
            'results': results
        }

        return data

    def __generate_results(self) -> list:
        # Compute the assessment table
        dimensions_total_relevance = DQDimension.objects.aggregate(Sum('relevance'))['relevance__sum']
        results = []
        assessment = self.dataset.dq_assessment
        ehds_categories = EHDSCategory.objects.all()

        for category_index, category in enumerate(ehds_categories, start=1):
            results.append({
                'category_index': category_index,  # Numeric index
                'category_index_str': f"{category_index}.",  # String version
                'name': category.name,
                'dimensions': [],
                'score': 0,
                'score_str': "0.00",  # String version of score
                'all_dimensions_ok': True,
                'id': category.id
            })

            dimensions = DQDimension.objects.filter(ehds_category=category)
            for dimension_index, dimension in enumerate(dimensions, start=1):
                dimension_relevance = (dimension.relevance / dimensions_total_relevance) * 100
                dimension_index_str = f"{category_index}.{dimension_index}."  # String version of index

                results[-1]['dimensions'].append({
                    'dimension_index': dimension_index,  # Numeric index
                    'dimension_index_str': dimension_index_str,  # String version
                    'name': dimension.name,
                    'definition': dimension.definition,
                    'relevance': dimension_relevance,
                    'relevance_str': f"{dimension_relevance:.2f}%",  # String version of relevance
                    'metrics': [],
                    'score': 0,
                    'score_str': "0.00",  # String version of score
                    'all_metrics_ok': True,
                    'id': dimension.id
                })

                metrics = DQMetric.objects.filter(dq_dimension=dimension)
                for metric_index, metric in enumerate(metrics, start=1):
                    metric_label = f"Metric #{metric_index}"
                    metric_value = DQMetricValue.objects.filter(dq_assessment=assessment, dq_metric=metric).first()
                    answer_text = "Not answered"

                    if metric_value:
                        # Fetch the corresponding text for the categorical value
                        answer_text = metric_value.value
                        if metric_value.value.isdigit():
                            category_match = DQCategoricalMetricCategory.objects.filter(
                                dq_categorical_metric=metric, value=int(metric_value.value)
                            ).first()
                            if category_match:
                                answer_text = category_match.text

                    results[-1]['dimensions'][-1]['metrics'].append({
                        'definition': metric.definition,
                        'weight': int(metric.weight),
                        'weight_str': f"{int(metric.weight)}%",  # String version of weight
                        'score': 0,
                        'score_str': "0.00",  # String version of score
                        'metric_label': metric_label,
                        'answer': answer_text,
                        'is_metric_ok': False
                    })

                    dq_metric_value = DQMetricValue.objects.filter(dq_assessment=assessment, dq_metric=metric)
                    current_value = None
                    metric_score = 0

                    if dq_metric_value.exists():
                        current_value = str(dq_metric_value.first().value)

                    if getattr(metric, 'dqcategoricalmetric') is not None and current_value:
                        current_value = int(current_value)
                        metric_categories = DQCategoricalMetricCategory.objects.filter(
                            dq_categorical_metric=metric
                        ).count()

                        # Calculate metric score
                        metric_score = current_value / (metric_categories - 1)
                        metric_score = metric_score * (metric.weight / 100) * dimension_relevance

                        # Store both numeric and string score
                        results[-1]['dimensions'][-1]['metrics'][-1]['report_URL'] = dq_metric_value.first().report_URL
                        results[-1]['dimensions'][-1]['metrics'][-1]['score'] = metric_score
                        results[-1]['dimensions'][-1]['metrics'][-1]['score_str'] = f"{metric_score:.2f}"
                        results[-1]['dimensions'][-1]['score'] += metric_score

                    results[-1]['dimensions'][-1]['metrics'][-1]['is_metric_ok'] = metric_score > 0
                    results[-1]['dimensions'][-1]['all_metrics_ok'] = results[-1]['dimensions'][-1]['all_metrics_ok'] and results[-1]['dimensions'][-1]['metrics'][-1]['is_metric_ok']

                # Store the formatted score for the dimension
                results[-1]['dimensions'][-1]['score_str'] = f"{results[-1]['dimensions'][-1]['score']:.2f}"

                results[-1]['all_dimensions_ok'] = results[-1]['all_dimensions_ok'] and results[-1]['dimensions'][-1]['all_metrics_ok']

            # Store the formatted score for the category
            results[-1]['score_str'] = f"{results[-1]['score']:.2f}"

        return results
