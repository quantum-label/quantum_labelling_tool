import pandas as pd
from django.db.models import Sum

from code.helpers.django import generate_assessment_stars
from webapp.models import Dataset, EHDSCategory, DQDimension, DQMetric, DQMetricValue, DQCategoricalMetricCategory
import plotly.express as px
import plotly.io as pio

import plotly.express as px
import plotly.io as pio

import plotly.express as px
import plotly.io as pio


import plotly.express as px
import plotly.io as pio

def plot_label(dataset: Dataset) -> str:
    elements = []
    parents = []
    values = []
    colors = {}

    scores, total_score = compute_scores(dataset=dataset)
    computed_score = total_score

    stars = generate_assessment_stars(
        total_score,
        empty_star='\u2606',
        filled_star='\u2605'
    )

    total_score = f'{total_score:.2f}'

    # Predefined color palette for categories
    category_colors = [
        (0, 68, 148),   # Dark Blue
        (255, 214, 23), # Yellow
        (64, 64, 64),   # Dark Grey
        (242, 151, 39)  # Orange
    ]

    category_index = 0  # Track category color assignment

    # Root Element
    elements.append('QUANTUM')
    parents.append('')
    values.append(computed_score)
    colors['QUANTUM'] = 'rgb(255, 255, 255)'  # White

    for category in EHDSCategory.objects.all():
        dimensions = DQDimension.objects.filter(ehds_category=category)

        category_score = scores[category.name]['score']
        category_max_score = scores[category.name]['relevance']
        category_name = f'{category.name}<br>{category_score:.2f}/{category_max_score:.2f}'

        elements.append(category_name)
        parents.append('QUANTUM')
        values.append(category_score)  # Use actual category score, not max score

        # Assign a color to the category
        base_color = category_colors[category_index % len(category_colors)]
        category_index += 1  # Increment for the next category

        # Store solid RGB color (full opacity) for the category
        category_color = f'rgb({base_color[0]},{base_color[1]},{base_color[2]})'
        colors[category_name] = category_color

        for dimension in dimensions:
            score = scores[category.name]['dimensions'][dimension.name]['score']
            max_score = scores[category.name]['dimensions'][dimension.name]['relevance'] * 100

            score_str = f'{score:.2f}'
            max_score_str = f'{max_score:.2f}'

            dimension_name = f'{dimension.name}<br>{score_str}/{max_score_str}'
            elements.append(dimension_name)
            parents.append(category_name)

            # Compute dimension opacity using the category's base color
            opacity = min(1.0, max(score / max_score, 0.3))  # Ensuring opacity is between 0.3 and 1.0
            rgba_color = f'rgba({base_color[0]},{base_color[1]},{base_color[2]},{opacity:.2f})'

            values.append(score)  # Use actual score, not max score
            colors[dimension_name] = rgba_color  # Assign color with opacity

    # Store color mapping explicitly in the dataset
    data = dict(
        elements=elements,
        parents=parents,
        values=values
    )

    # Create sunburst plot
    figure = px.sunburst(
        data,
        names='elements',
        parents='parents',
        values='values',
        branchvalues='total',
        color='elements',
        color_discrete_map=colors  # Uses the defined RGBA colors
    )

    figure.update_layout(
        images=[dict(
            source='https://pbs.twimg.com/profile_images/1757761164556021760/WK-zxj8K_400x400.jpg',
            xref='paper', yref='paper',
            x=0.5, y=0.55,
            sizex=0.18, sizey=0.18,
            xanchor='center', yanchor='middle',
            layer='above'
        )],
    )

    figure.add_annotation(
        dict(
            font=dict(color='black', size=15),
            xref='paper', yref='paper',
            x=0.5, y=0.43,
            showarrow=False,
            text=f'{stars}<br>{total_score}/100',
            textangle=0,
            xanchor='center',
        )
    )

    figure.update_traces(hovertemplate='Score: %{value:.2f}')

    figure.update_layout(
        margin=dict(t=0, l=0, r=0, b=0)
    )

    # Generate HTML div as a string
    html_div = pio.to_html(
        figure,
        default_width='100%',
        include_plotlyjs='cdn',
        full_html=False,
        config={'staticPlot': False}
    )

    return html_div


def compute_scores(dataset: Dataset) -> [dict, float]:
    # Compute the assessment table
    dimensions_total_relevance = DQDimension.objects.aggregate(Sum('relevance'))['relevance__sum']

    results = {}
    total_score = 0
    assessment = dataset.dq_assessment
    ehds_categories = EHDSCategory.objects.all()
    for category in ehds_categories:
        results[category.name] = {
            'relevance': 0,
            'dimensions': {},
            'score': 0
        }

        dimensions = DQDimension.objects.filter(ehds_category=category)
        for dimension in dimensions:
            dimension_relevance = (dimension.relevance / dimensions_total_relevance)
            results[category.name]['dimensions'][dimension.name] = {
                'relevance': dimension_relevance,
                # this part take care of showing the number of stars in the dashboard (removed the *100 cause I increase the metrics weight by 100)
                'metrics': {},
                'score': 0
            }
            results[category.name]['relevance'] += (dimension_relevance * 100)

            metrics = DQMetric.objects.filter(dq_dimension=dimension)
            for metric_index, metric in enumerate(metrics):
                results[category.name]['dimensions'][dimension.name]['metrics'][metric.definition] = {
                    'weight': int(metric.weight),
                    'score': 0
                }
                metric_score = 0

                dq_metric_value = DQMetricValue.objects.filter(dq_assessment=assessment, dq_metric=metric)

                # If the metric is filled then we assign the value, else it is None
                if len(dq_metric_value) >= 1:
                    current_value = str(dq_metric_value.first().value)

                    # For the categorical metrics we provide the possible values
                    if getattr(metric, 'dqcategoricalmetric') is not None and current_value:
                        current_value = int(current_value)
                        metric_categories = DQCategoricalMetricCategory.objects.filter(
                            dq_categorical_metric=metric
                        ).count()

                        metric_score = current_value / (metric_categories - 1)  # If 3 : 0, 1, 2 -> 0% 50% 100%
                    metric_score = metric_score * metric.weight * results[category.name]['dimensions'][dimension.name][
                        'relevance']
                    results[category.name]['dimensions'][dimension.name]['metrics'][metric.definition][
                        'score'] = metric_score
                    results[category.name]['dimensions'][dimension.name]['score'] += metric_score
                    results[category.name]['score'] += metric_score

            total_score += results[category.name]['dimensions'][dimension.name]['score']

    return results, total_score
