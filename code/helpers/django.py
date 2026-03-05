from typing import Optional, Tuple

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect

from webapp.models import UserOrganization, Dataset, Catalogue


def redirect_with_message(
        request: HttpRequest,
        redirect_url: str,
        message: str,
        message_type: int = messages.INFO
) -> HttpResponseRedirect:
    messages.add_message(
        request,
        message_type,
        message
    )

    return redirect(redirect_url)


def generate_assessment_stars(score: float, empty_star='&star;',
                              filled_star='&starf;') -> str:
    number_of_stars = compute_amount_of_stars(score)
    stars_html = ''

    for star in range(0, number_of_stars):
        stars_html += filled_star

    for star in range(number_of_stars, 5):
        stars_html += empty_star

    return stars_html


def compute_amount_of_stars(score: float):
    if score < 25:
        return 0
    elif score < 45:
        return 1
    elif score < 60:
        return 2
    elif score < 80:
        return 3
    elif score < 90:
        return 4

    return 5


def is_user_allowed_to_access(
        request: HttpRequest,
        user: User,
        dataset_id_to_check: Optional[int] = None,
        catalogue_id_to_check: Optional[int] = None
) -> Tuple[bool, Optional[HttpResponseRedirect]]:
    """
    Precondition to check if user has access. Also can be checked if a dataset id or catalogue id is accessible to the user.

    """
    user_organization = UserOrganization.objects.filter(user=user)

    if len(user_organization) == 0:
        return False, redirect_with_message(
            request,
            '/',
            'User not associated to an organization. Please, contact administrator.'
        )

    user_organization = user_organization.first()
    organization = user_organization.organization

    if dataset_id_to_check is not None:
        dataset = Dataset.objects.filter(id=dataset_id_to_check)

        if len(dataset) == 0:
            return False, redirect_with_message(
                request,
                '/dashboard',
                'Dataset accessed doesn\'t exist'
            )

        dataset = dataset.first()

        if dataset.organization.id != organization.id:
            return False, redirect_with_message(
                request,
                '/dashboard',
                'No access permission for this dataset'
            )

    if catalogue_id_to_check is not None:
        catalogue = Catalogue.objects.filter(id=catalogue_id_to_check)

        if len(catalogue) == 0:
            return False, redirect_with_message(
                request,
                '/dashboard',
                'Catalogue accessed doesn\'t exist'
            )

        catalogue = catalogue.first()

        if catalogue.user.id != user.id:
            return False, redirect_with_message(
                request,
                '/dashboard',
                'No access permission for this catalogue'
            )

    return True, None
