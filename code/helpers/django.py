import json

from django.contrib import messages
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect


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


def load_glossary() -> dict:
    try:
        glossary_file = open('documentation/glossary.json')
        glossary = json.load(glossary_file)
        glossary_file.close()

        return glossary
    except:
        import traceback
        traceback.print_exc()
        print('Failed loading the glossary!')

    return {}
