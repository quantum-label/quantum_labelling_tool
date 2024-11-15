import json
import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from code.fdp.constants import FDP_DEVELOPMENT_URL
from code.fdp.fdp import create_catalogue, publish_catalogue
from code.helpers.django import redirect_with_message, generate_assessment_stars
from code.label.label import plot_label, compute_scores
from code.rdf.ttl_templating import template_catalogue, generate_ttl_file
# from code.rdf.ttl_templating import template_catalogue, fill_full_template
from webapp.models import Dataset, DQAssessment, DQMetric, DQMetricValue, EHDSCategory, DQDimension, \
    DQCategoricalMetricCategory, Organization, UserOrganization, Catalogue, MaturityDimension, MaturityDimensionLevel, \
    MaturityDimensionValue


# Create your views here.
def home_view(request: HttpRequest) -> HttpResponse:
    """
    Home web page
    :param request:
    :return:
    """
    # Render home html
    return render(
        request,
        'home.html'
    )


def about_view(request: HttpRequest) -> HttpResponse:
    """
    About web page
    :param request:
    :return:
    """
    # Render home html
    return render(
        request,
        'about.html'
    )


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Login web page
    :param request:
    :return:
    """
    # If it is a POST it is a login attempt
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if username is None or password is None:
            return redirect_with_message(request, '/login', 'Please, fill all fields!')

        # Check if user exists and the credentials are valid
        user = authenticate(request, username=username, password=password)

        # If user exists it logs in
        if user is not None:
            login(request, user)

            return redirect('/dashboard')
        # Else it produces an informative message and redirects to the login web page
        else:
            return redirect_with_message(request, '/login', 'Wrong user/password combination!')
    # If it is a GET renders the login html
    elif request.method == 'GET':
        return render(
            request,
            'login.html'
        )
    # If it is other request redirects to home
    else:
        return redirect('/')


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Log out endpoint
    :param request:
    :return:
    """
    # Logs out a logged in user
    logout(request)

    return redirect_with_message(
        request,
        '/login',
        f'Logged out successfully!'
    )


@login_required
def user_dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    Shows the user datasets' web page

    :param request:
    :return:
    """
    if request.method == 'GET':
        # Get the user from
        user = request.user

        # Get the user organization and its datasets
        user_organization = UserOrganization.objects.filter(user=user)

        if len(user_organization) == 0:
            return redirect_with_message(
                request,
                '/',
                'User not associated to an organization. Please, contact administrator: pilot@quantumproject.eu .'
            )

        user_organization = user_organization.first()

        datasets = Dataset.objects.filter(organization=user_organization.organization)

        dataset_list = []

        # Make a list of the datasets and the assessment filled fields ratio
        for dataset in datasets:
            assessment = DQAssessment.objects.filter(dataset=dataset).first()

            metrics = DQMetric.objects.all().count()
            dq_metric_value_amount = DQMetricValue.objects.filter(dq_assessment=assessment).count()

            _, score = compute_scores(dataset)
            score = int(score)
            stars = generate_assessment_stars(score)

            if metrics == dq_metric_value_amount:
                stars_class = 'btn-success'
            else:
                stars_class = 'btn-warning'

            assessment_text = 'Start'

            if dq_metric_value_amount > 0:
                assessment_text = f'Edit'
                # assessment_text = f'Edit ({dq_metric_value_amount}/{metrics})'

            dataset_list.append({
                'id': dataset.id,
                'user': dataset.catalogue.user.username,
                'catalogue': dataset.catalogue.title,
                'name': dataset.name,
                'description': dataset.description,
                'version': dataset.version,
                'assessment_percentage': assessment_text,
                'stars': stars,
                'score': score,
                'stars_class': stars_class
            })

        catalogues = Catalogue.objects.filter(user=user)

        return render(
            request,
            'dq_dashboard.html',
            context={
                'datasets': dataset_list,
                'catalogues': catalogues,
                'organization': user_organization.organization.name
            }
        )
    else:
        return redirect('/')


@login_required
def user_dataset_assessment_view(request: HttpRequest) -> HttpResponse:
    """
    Shows the web page of a dataset assessment
    :param request:
    :return:
    """
    # The GET request gets all the EHDS categories, dimensions, metrics and filled values to show
    if request.method == 'GET':
        user = request.user
        dataset_id = request.GET.get('id', None)

        dataset = Dataset.objects.filter(id=dataset_id)
        if len(dataset) == 0:
            return redirect_with_message(
                request,
                '/dashboard',
                'Dataset accessed doesn\'t exist'
            )
        dataset = dataset.first()

        assessment = DQAssessment.objects.filter(dataset=dataset).first()
        ehds_categories = EHDSCategory.objects.all()

        values = {}

        # We fill the dictionary with all the information to build the web page
        for category_index, category in enumerate(ehds_categories):
            values[category.name] = {
                'id': category.id,
                'name': f'{category_index + 1}. {category.name}',
                'dimensions': []
            }

            dimensions = DQDimension.objects.filter(ehds_category=category)
            for dimension_index, dimension in enumerate(dimensions):
                values[category.name]['dimensions'].append({
                    'id': dimension.id,
                    'name': f'{category_index + 1}.{dimension_index + 1}. {dimension.name}',
                    'definition': dimension.definition,
                    'relevance': dimension.relevance,
                    'metrics': []
                })

                metrics = DQMetric.objects.filter(dq_dimension=dimension)
                for index, metric in enumerate(metrics):
                    metric_label = f"Metric #{index + 1}"
                    dq_metric_value = DQMetricValue.objects.filter(dq_assessment=assessment, dq_metric=metric)
                    current_value = None

                    # If the metric is filled then we assign the value, else it is None
                    if len(dq_metric_value) >= 1:
                        current_value = str(dq_metric_value.first().value)

                    values[category.name]['dimensions'][-1]['metrics'].append({
                        'id': metric.id,
                        'name': metric.name,
                        'metric_label': metric_label,
                        'definition': metric.definition,
                        'additional_information': metric.additional_information,
                        'measurement_approach': metric.measurement_approach,
                        'formula': metric.formula,
                        'weight': metric.weight,
                        'value': current_value
                    })

                    # For the categorical metrics we provide the possible values
                    if getattr(metric, 'dqcategoricalmetric') is not None:
                        metric_category_values = []

                        metric_categories = DQCategoricalMetricCategory.objects.filter(dq_categorical_metric=metric)
                        for metric_category in metric_categories:
                            metric_category_values.append({
                                'value': str(metric_category.value),
                                'text': metric_category.text
                            })

                        values[category.name]['dimensions'][-1]['metrics'][-1][
                            'metric_category_values'] = metric_category_values

        return render(
            request,
            'dq_assessment.html',
            context={
                'dataset': dataset,
                'values': values.items(),
                'dataset_id': dataset_id
            }
        )
    # If it is a POST it is an update of the assessment values
    elif request.method == 'POST':
        post_keys = request.POST.keys()
        dataset_id = request.POST.get('dataset', None)

        if not dataset_id:
            # No assessment id provided
            return redirect_with_message(
                request,
                '/dashboard',
                'Dataset id not provided.'
            )

        dataset = Dataset.objects.get(id=dataset_id)

        # We search for the "metric_" keys in the POST dictionary
        metrics = []
        for key in post_keys:
            if key.startswith('metric_'):
                metric_key = key.replace('metric_', '')
                metric_value = request.POST.get(key)

                if len(metric_value) >= 1:
                    metric_value = metric_value[0]
                else:
                    continue

                # If metric value is not "empty"
                if metric_value != '-' and metric_value != '':
                    metrics.append(
                        (metric_key, metric_value)
                    )
        assessment = dataset.dq_assessment

        # We create or update the filled values
        changes = []
        for metric in metrics:
            dq_metric = DQMetric.objects.filter(id=metric[0]).first()

            value = metric[1]
            dq_metric_value, created = DQMetricValue.objects.get_or_create(
                dq_assessment=assessment,
                dq_metric=dq_metric
            )

            if dq_metric_value.value != value:
                changes.append(dq_metric.dq_dimension.name)

            dq_metric_value.value = value

            dq_metric_value.save()

        changes = set(changes)
        changes_message = ''

        if len(changes) > 0:
            changes_message = f'''
                The assessment for dataset {dataset.name}  has been updated!
                <br>
                Changes in dimensions:
            '''

            for change in changes:
                changes_message += f'<br> - {change}'

        # TODO: Update the FDP metric values
        ##############
        # Assessment
        # dataset = assessment.dataset
        #
        # ttl = fill_full_template(
        #     dataset=dataset,
        #     username=request.user.username
        # )
        #
        # dataset.rdf = ttl
        # dataset.save()
        ##############

        return redirect_with_message(
            request,
            f'/dataset/assessment?id={dataset_id}',
            changes_message
        )
    else:
        return redirect('/')


@login_required
def dataset_create_view(request: HttpRequest) -> HttpResponse:
    """
    Shows the dataset creation web page
    :param request:
    :return:
    """
    # If it is a GET it shows the web page
    if request.method == 'GET':
        user = request.user
        catalogues = Catalogue.objects.filter(user=user)

        if len(catalogues) == 0:
            return redirect_with_message(
                request,
                '/dashboard',
                'To create a dataset you need first to create a catalogue.'
            )

        return render(
            request,
            'dataset_create.html',
            context={
                'catalogues': catalogues
            }
        )
    # If it is a POST its the form filled
    elif request.method == 'POST':
        user = request.user
        dataset_name = request.POST.get('dataset_name', None)
        dataset_description = request.POST.get('dataset_description', None)
        dataset_catalogue_id = request.POST.get('dataset_catalogue', None)
        dataset_URI = request.POST.get('dataset_URI', None)

        organization = UserOrganization.objects.filter(user=user).first().organization
        catalogue = Catalogue.objects.filter(id=dataset_catalogue_id).first()

        # Sanity check. All the needed fields are filled
        if dataset_description is None \
                or dataset_name is None:
            return redirect_with_message(
                request,
                '/dataset/create',
                'Please fill all the fields.'
            )

        # Check if dataset exists with same name and version
        exists_duplicated_dataset = Dataset.objects.filter(
            name=dataset_name,
            version=1,
            organization=organization,
            catalogue=catalogue
        ).exists()

        # If the dataset is duplicated we make a redirect with a message
        if exists_duplicated_dataset:
            return redirect_with_message(
                request,
                '/dashboard',
                'A dataset with that name, catalogue and version already exists.'
            )

        # Else we create the dataset and its associated assessment
        else:
            dataset = Dataset(
                URI=dataset_URI,
                name=dataset_name,
                description=dataset_description,
                version=1,
                organization=organization,
                catalogue=catalogue
            )

            dq_assessment = DQAssessment(
                start_date=datetime.now()
            )
            dq_assessment.save()

            dataset.dq_assessment = dq_assessment
            # The dataset is truly created when the save operation is made
            dataset.save()

            # TODO: Create the dataset and assessment on the FDP
            ##############

            ##############

            return redirect_with_message(
                request,
                '/dashboard',
                f'Dataset "{dataset.name}" created!'
            )

    return redirect('/')


@login_required
def dataset_modify_view(request: HttpRequest) -> HttpResponse:
    """
    Shows the dataset modification web page
    :param request:
    :return:
    """
    # If it is a GET it shows the web page
    if request.method == 'GET':
        user = request.user
        dataset_id = request.GET.get('id', None)

        if dataset_id is None:
            return redirect_with_message(
                request,
                '/dashboard',
                'No dataset id provided.'
            )

        dataset = Dataset.objects.filter(id=dataset_id)

        if len(dataset) == 0:
            return redirect_with_message(
                request,
                '/dashboard',
                'Dataset id provided does not exist.'
            )

        dataset = dataset.first()

        catalogue = Catalogue.objects.get(dataset=dataset)
        catalogues = Catalogue.objects.filter(user=user)

        return render(
            request,
            'dataset_modify.html',
            context={
                'dataset': dataset,
                'catalogue': catalogue,
                'catalogues': catalogues
            }
        )
    # If it is a POST its the form filled
    elif request.method == 'POST':
        user = request.user
        dataset_id = request.POST.get('dataset_id', None)
        dataset_name = request.POST.get('dataset_name', None)
        dataset_description = request.POST.get('dataset_description', None)
        dataset_URI = request.POST.get('dataset_URI', None)

        # Sanity check. All the needed fields are filled
        if dataset_id is None \
                or dataset_name is None \
                or dataset_description is None:
            return redirect_with_message(
                request,
                '/dataset/modify',
                'Please fill all the fields.'
            )

        # Else we create the dataset and its associated assessment
        else:
            dataset = Dataset.objects.get(id=dataset_id)

            if not dataset:
                return redirect_with_message(
                    request,
                    '/catalogue/modify',
                    'Dataset id not existing.'
                )

            dataset.name = dataset_name
            dataset.description = dataset_description
            dataset.URI = dataset_URI

            dataset.save()

            # TODO: Create the catalogue and assessment on the FDP
            ##############

            ##############

            return redirect_with_message(
                request,
                '/dashboard',
                f'Dataset "{dataset.name}" modified!'
            )

    return redirect('/')


@login_required
def dataset_delete_view(request: HttpRequest) -> HttpResponse:
    """
    Deletes a dataset given the id
    :param request:
    :return:
    """

    if request.method == 'GET':
        user = request.user
        # catalogues = Catalogue.objects.filter(user=user)
        dataset_id = request.GET.get('id', None)

        if not dataset_id:
            return redirect_with_message(
                request,
                '/dashboard',
                'No dataset ID provided.'
            )

        dataset = Dataset.objects.filter(id=dataset_id).first()

        if not dataset:
            return redirect_with_message(
                request,
                '/dashboard',
                'Dataset ID provided does not exist.'
            )

        # Ensure the user is authorized to delete this dataset
        if user != dataset.catalogue.user:
            return redirect_with_message(
                request,
                '/dashboard',
                'You are not authorized to delete this dataset.'
            )

        dataset.delete()

        return redirect_with_message(
            request,
            '/dashboard',
            f'Dataset "{dataset.name}" deleted successfully.'
        )

    return redirect('/dashboard')


@login_required
def catalogue_create_view(request: HttpRequest) -> HttpResponse:
    """
    Shows the catalogue creation web page
    :param request:
    :return:
    """
    # If it is a GET it shows the web page
    if request.method == 'GET':
        return render(
            request,
            'catalogue_create.html'
        )
    # If it is a POST its the form filled
    elif request.method == 'POST':
        user = request.user
        catalogue_title = request.POST.get('catalogue_title', None)
        catalogue_version = request.POST.get('catalogue_version', None)

        # Sanity check. All the needed fields are filled
        if catalogue_title is None \
                or catalogue_version is None:
            return redirect_with_message(
                request,
                '/catalogue/create',
                'Please fill all the fields.'
            )

        # Check if catalogue exists with same name and version
        exists_duplicated_catalogue = Catalogue.objects.filter(
            title=catalogue_title,
            version=catalogue_version,
            user=user
        ).exists()

        # If the catalogue is duplicated we make a redirect with a message
        if exists_duplicated_catalogue:
            return redirect_with_message(
                request,
                '/dashboard',
                'A catalogue with that title and version already exists for this user.'
            )

        # Else we create the dataset and its associated assessment
        else:
            catalogue = Catalogue(
                title=catalogue_title,
                version=catalogue_version,
                user=user,
                part_of=os.getenv('FDP_URL', FDP_DEVELOPMENT_URL),
            )
            catalogue.save()
            # TODO: Create the catalogue and assessment on the FDP
            ##############
            # # Template catalogue
            # catalogue_template = template_catalogue(
            #     catalogue=catalogue,
            #     username=user.username
            # )
            # # Create catalogue
            # catalogue_id = create_catalogue(
            #     rdf_content=catalogue_template
            # )
            # if catalogue_id:
            #     # Publish catalogue
            #     status_code, _ = publish_catalogue(
            #         catalogue_id=catalogue_id
            #     )
            #     print(status_code)
            #     # Store on model
            #     if status_code == 200:
            #         catalogue.fdp_id = catalogue_id
            #         catalogue.save()
            #     else:
            #         return redirect_with_message(
            #             request,
            #             '/dashboard',
            #             f'Catalogue "{catalogue.title}" could not be created. Check Fair Data Point connection!'
            #         )
            # else:
            #     return redirect_with_message(
            #         request,
            #         '/dashboard',
            #         f'Catalogue "{catalogue.title}" could not be created. Check Fair Data Point connection!'
            #     )
            ##############

            return redirect_with_message(
                request,
                '/dashboard',
                f'Catalogue "{catalogue.title}" created!'
            )

    return redirect('/')


@login_required
def catalogue_modify_view(request: HttpRequest) -> HttpResponse:
    """
    Shows the catalogue modification web page
    :param request:
    :return:
    """
    # If it is a GET it shows the web page
    if request.method == 'GET':
        catalogue_id = request.GET.get('id', None)

        if catalogue_id is None:
            return redirect_with_message(
                request,
                '/dashboard',
                'No catalogue id was provided.'
            )

        catalogue = Catalogue.objects.filter(id=catalogue_id)

        if len(catalogue) == 0:
            return redirect_with_message(
                request,
                '/dashboard',
                'Catalogue id provided not existing.'
            )

        catalogue = catalogue.first()

        return render(
            request,
            'catalogue_modify.html',
            context={
                'catalogue': catalogue
            }
        )
    # If it is a POST its the form filled
    elif request.method == 'POST':
        user = request.user
        catalogue_id = request.POST.get('catalogue_id', None)
        catalogue_title = request.POST.get('catalogue_title', None)
        catalogue_version = request.POST.get('catalogue_version', None)

        # Sanity check. All the needed fields are filled
        if catalogue_title is None \
                or catalogue_id is None \
                or catalogue_version is None:
            return redirect_with_message(
                request,
                '/catalogue/modify',
                'Please fill all the fields.'
            )

        # Else we create the dataset and its associated assessment
        else:
            catalogue = Catalogue.objects.get(id=catalogue_id)

            if not catalogue:
                return redirect_with_message(
                    request,
                    '/catalogue/modify',
                    'Catalogue id not existing.'
                )

            catalogue.title = catalogue_title
            catalogue.version = catalogue_version

            # The catalogue is truly created when the save operation is made
            catalogue.save()

            # TODO: Update the catalogue and assessment on the FDP
            ##############

            ##############

            return redirect_with_message(
                request,
                '/dashboard',
                f'Catalogue "{catalogue.title}" modified!'
            )

    return redirect('/')


@login_required
def catalogue_delete_view(request: HttpRequest) -> HttpResponse:
    """
    Deletes a catalogue based on the provided id.
    :param request:
    :return:
    """
    if request.method == 'GET':
        user = request.user
        # Get the catalogue ID from the request
        catalogue_id = request.GET.get('id', None)

        # If no ID is provided, redirect to the dashboard with an error message
        if not catalogue_id:
            return redirect_with_message(
                request,
                '/dashboard',
                'No catalogue ID provided.'
            )

        # Find the catalogue by ID
        catalogue = Catalogue.objects.filter(id=catalogue_id).first()

        # If the catalogue does not exist, return an error
        if not catalogue:
            return redirect_with_message(
                request,
                '/dashboard',
                'Catalogue ID provided does not exist.'
            )

        # Ensure the user is authorized to delete this catalogue
        if request.user != catalogue.user:
            return redirect_with_message(
                request,
                '/dashboard',
                'You are not authorized to delete this catalogue.'
            )

        # Delete the catalogue
        catalogue.delete()

        # Redirect to the dashboard with a success message
        return redirect_with_message(
            request,
            '/dashboard',
            f'Catalogue "{catalogue.title}" deleted successfully.'
        )

    return redirect('/dashboard')


def dataset_label_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        dataset_id = request.GET.get('id', None)

        if dataset_id is None:
            return redirect_with_message(
                request,
                '/dashboard',
                f'Dataset not provided!'
            )

        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except:
            return redirect_with_message(
                request,
                '/dashboard',
                f'Dataset not existing!'
            )

        # Compute the label plot
        label = plot_label(dataset)

        # Compute the assessment table
        dimensions_total_relevance = DQDimension.objects.aggregate(Sum('relevance'))[
            'relevance__sum']  # DQDimension.objects: This refers to all records (or rows) in the DQDimension table (or model). It allows you to query or manipulate the data related to this model in the database. aggregate(): This is a method in Django ORM used for performing aggregate functions (such as sum, average, count) on a set of data.
        # When using aggregate() in Django, it returns a dictionary where the keys are based on the fields and operations you're performing. In your case, Sum('relevance') creates a key 'relevance__sum', and to get the actual sum, you access the dictionary value using this key.
        results = []  # This list will store the results for each category, dimension, and metric.
        total_score = 0  # This will accumulate the total score across all dimensions and metrics.
        assessment = dataset.dq_assessment
        ehds_categories = EHDSCategory.objects.all()  # This retrieves all EHDS categories, which will be iterated over to calculate the score for each category and its associated dimensions and metrics.
        for category in ehds_categories:
            results.append({
                'name': category.name,
                'dimensions': [],
                'score': 0  # Initialized to 0. This will accumulate the total score for the category.
            })

            dimensions = DQDimension.objects.filter(ehds_category=category)
            for dimension in dimensions:
                results[-1]['dimensions'].append({
                    # why the -1? --> In Python, -1 is an index that refers to the last element in a list. In this case, results[-1] is referring to the most recent category that was added to the results list. MORE INFO: e use results[-1] is because we want to add dimensions to the current category being processed in the loop. When you start processing a new category (from EHDSCategory), you first append the category to the results list. Then, within that same loop, you start adding dimensions to the dimensions list within that newly appended category. Since you’re still processing the last category added, you access it via results[-1]. Without -1, we wouldn’t know which category to add dimensions to, and Python doesn’t have direct references to the most recently appended item without such indexing.
                    'name': dimension.name,
                    'relevance': (dimension.relevance / dimensions_total_relevance) * 100,
                    # (inside the table of the label page) this formula make the dimension scores from decimal (0.1) to percentage (10) --> affecting also the numbers of stars since you would add 0.1 instead of 10
                    'metrics': [],
                    'score': 0
                })

                metrics = DQMetric.objects.filter(dq_dimension=dimension)
                for metric_index, metric in enumerate(metrics):
                    results[-1]['dimensions'][-1]['metrics'].append({
                        'definition': metric.definition,
                        'weight': int(metric.weight),
                        # #this part shows metrics weights inside the table of the label page. (removed the *100 cause I increase the metrics weight by 100)
                        'score': 0
                    })

                    dq_metric_value = DQMetricValue.objects.filter(dq_assessment=assessment,
                                                                   dq_metric=metric)  # This retrieves the metric values related to the current assessment and metric.
                    current_value = None  # can you use also 0 instead of none? --> Yes, you can use 0 instead of None. However, in this case, the author is using None to indicate that the value is not set. If the value is set, it will be a string. If it is not set, it will be None.

                    # If the metric is filled then we assign the value, else it is None
                    if len(dq_metric_value) >= 1:  # If there's at least one metric value (len(dq_metric_value) >= 1), the current value is extracted using .first().
                        current_value = str(dq_metric_value.first().value)
                    else:
                        pass

                    # For the categorical metrics we provide the possible values
                    if getattr(metric,
                               'dqcategoricalmetric') is not None and current_value:  # If the metric is not a categorical metric (i.e., doesn't have this attribute), getattr will return None, so this ensures that we only proceed if it is indeed a categorical metric. Then This checks if current_value has been assigned a value (i.e., it's not None or empty). If current_value is valid, we proceed with calculating the score.
                        current_value = int(current_value)
                        metric_categories = DQCategoricalMetricCategory.objects.filter(
                            dq_categorical_metric=metric
                        ).count()  # This checks if the current metric is a categorical metric (i.e., it has multiple pre-defined values).

                        metric_score = current_value / (
                                metric_categories - 1)  # If 3 : 0, 1, 2 -> 0% 50% 100% + --> This part normalizes the current value. If you have 3 categories (e.g., 0 = Low, 1 = Medium, 2 = High), you would divide by 2 (i.e., metric_categories - 1), to convert the current value into a percentage scale (0%, 50%, 100%).
                        metric_score = metric_score * (metric.weight / 100) * results[-1]['dimensions'][-1][
                            'relevance']  # This step takes the normalized score (current_value / (metric_categories - 1)) from the previous line and adjusts it further based on the weight of the metric and the relevance of the dimension.
                        results[-1]['dimensions'][-1]['metrics'][-1][
                            'score'] = metric_score  # here we assign the metric score above calculated to the score key of the last metric in the last dimension of the last category.
                        results[-1]['dimensions'][-1][
                            'score'] += metric_score  # here we add the metric score above calculated to the score key of the last dimension in the last category. this is because the dimension score is calculated as the sum of all metric scores within that dimension.

                total_score += results[-1]['dimensions'][-1][
                    'score']  # This is exactly line 774 above and adds the score of the last dimension (just calculated) to the total score for all dimensions and categories.

        # Drawing the stars
        stars_element = generate_assessment_stars(total_score)

        return render(
            request,
            'dataset_label.html',
            context={
                'label': label,
                'results': results,
                'score': total_score,
                'stars': stars_element,
                'dataset_id': dataset_id
            }
        )
    else:
        return redirect_with_message(
            request,
            '/dashboard',
            f'Wrong access!'
        )


@login_required
def organization_maturity_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        user = request.user

        # Get the user organization and its datasets
        user_organization = UserOrganization.objects.filter(user=user)

        if len(user_organization) == 0:
            return redirect_with_message(
                request,
                '/',
                'User not associated to an organization. Please, contact administartor: pilot@quantumproject.eu .'
            )

        user_organization = user_organization.first().organization

        matrix_score = 0

        dimensions = MaturityDimension.objects.all()
        dimensions_dictionary = {}

        for dimension in dimensions:
            dimensions_dictionary[dimension.name] = {
                'id': dimension.id,
                'definition': dimension.definition,
                'options': [],
                'value': None
            }

            levels = MaturityDimensionLevel.objects.filter(maturity_dimension=dimension)

            for level in levels:
                dimensions_dictionary[dimension.name]['options'].append({
                    'value': level.value,
                    'text': level.text
                })

            dimension_value = MaturityDimensionValue.objects.filter(
                maturity_dimension=dimension,
                maturity_organization=user_organization
            )

            if len(dimension_value) == 1:
                dimensions_dictionary[dimension.name]['value'] = dimension_value.first().maturity_dimension_level.value
                matrix_score += dimension_value.first().maturity_dimension_level.value

        return render(
            request,
            'maturity_dashboard.html',
            context={
                'dimensions': dimensions_dictionary,
                'score': matrix_score,
                'total_score': 5 * 10,
                'organization': user_organization.name
            }
        )
    elif request.method == 'POST':
        post_keys = request.POST.keys()
        user = request.user
        user_organization = UserOrganization.objects.get(user=user).organization

        # We search for the "dimension_" keys in the POST dictionary
        dimensions = []
        for key in post_keys:
            if key.startswith('dimension_value_'):
                dimension_key = key.replace('dimension_value_', '')
                dimension_value = request.POST.get(key)

                if len(dimension_value) >= 1:
                    dimension_value = dimension_value[0]
                else:
                    continue

                # If metric value is not "empty"
                if dimension_value != '-' and dimension_value != '':
                    dimensions.append(
                        (dimension_key, dimension_value)
                    )

        # We create or update the filled values
        changes = []
        for dimension in dimensions:
            maturity_dimension = MaturityDimension.objects.get(id=dimension[0])

            value = int(dimension[1])

            maturity_dimension_level = MaturityDimensionLevel.objects.get(
                maturity_dimension=maturity_dimension,
                value=value
            )

            maturity_dimension_value, created = MaturityDimensionValue.objects.get_or_create(
                maturity_dimension=maturity_dimension,
                maturity_organization=user_organization
            )

            if maturity_dimension_value.maturity_dimension_level is None or \
                    maturity_dimension_value.maturity_dimension_level.value != value:
                changes.append(maturity_dimension.name)

            maturity_dimension_value.maturity_dimension_level = maturity_dimension_level

            maturity_dimension_value.save()

        changes = set(changes)
        changes_message = ''

        if len(changes) > 0:
            changes_message = f'''
                The organization maturity matrix has changed!
                <br>
                Changes in dimensions:
            '''

            for change in changes:
                changes_message += f'<br> - {change}'

        return redirect_with_message(
            request,
            '/organization/maturity',
            changes_message
        )
    else:
        return redirect_with_message(
            request,
            '/dashboard',
            f'Wrong access!'
        )


def download_assessment_rdf(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        user = request.user
        dataset_id = request.GET.get('id', None)

        dataset = Dataset.objects.filter(id=dataset_id)
        if len(dataset) == 0:
            return redirect_with_message(
                request,
                '/dashboard',
                'Dataset accessed doesn\'t exist'
            )
        dataset = dataset.first()

        catalogue = dataset.catalogue
        assessment = DQAssessment.objects.filter(dataset=dataset).first()

        ttl_file = generate_ttl_file(
            catalogue=catalogue,
            dataset=dataset,
            username=user.username
        )

        response = HttpResponse(ttl_file, content_type='application/text charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="rdf.ttl"'

        return response
    else:
        return redirect_with_message(
            request,
            '/dashboard',
            f'Wrong access!'
        )