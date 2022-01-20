import base64
import hashlib

from django import template
from django.conf import settings
from django.utils.html import mark_safe
from django.contrib.staticfiles import finders
from django.templatetags.static import static

from ..models import InformationObject, Questionaire, Report
from ..forms import QuestionaireForm

register = template.Library()


def sha384(filepath):
    sha = hashlib.sha384()
    with open(filepath, "rb") as f:
        while True:
            block = f.read(1024)
            if not block:
                break
            sha.update(block)
        return sha.digest()


def subresource_integrity(filepath):
    sha = sha384(filepath)
    return "sha384-" + base64.b64encode(sha).decode("utf-8")


@register.simple_tag
def output_static(path):
    result = finders.find(path)
    with open(result) as f:
        return mark_safe(f.read())


@register.simple_tag
def script_tag(path):
    url = static(path)
    if not url.startswith("http"):
        url = settings.SITE_URL + url
    filepath = finders.find(path)
    sri = subresource_integrity(filepath)
    return mark_safe(
        '<script src="{url}" integrity="{sri}" crossorigin="anonymous" '
        "async></script>".format(url=url, sri=sri)
    )


@register.filter
def request_population_ratio(value):
    if isinstance(value, dict):
        req = value["request_count"]
        pop = value["population"]
    else:
        req = value.request_count
        pop = value.population
    if value and pop:
        return round(req / pop * 100_000, 1)


@register.filter
def in_mio(value):
    if value:
        return round(value / 1_000_000, 2)


@register.filter
def foirequest_has_questionaire(foirequest):
    if not foirequest.campaign:
        return False
    if not foirequest.campaign.has_reporting:
        return False

    return True


@register.inclusion_tag("froide_campaign/_questionaire.html")
def render_campaign_questionaire(foirequest):
    iobj = InformationObject.objects.filter(foirequests=foirequest).first()
    if not iobj:
        return None

    questionaire = Questionaire.objects.filter(campaign=iobj.campaign).first()
    if not questionaire:
        return None

    reports = list(
        Report.objects.filter(questionaire=questionaire, foirequest=foirequest)
    )
    initial_data = {}
    if not questionaire.multiple_reports and reports:
        report = reports[-1]
        initial_data = {
            "field_{}".format(a.question_id): a.text for a in report.answer_set.all()
        }

    form = QuestionaireForm(questionaire=questionaire, initial=initial_data)

    return {
        "questionaire": questionaire,
        "foirequest": foirequest,
        "report_count": len(reports),
        "iobj": iobj,
        "form": form,
    }


@register.filter
def foirequest_campaign_report_count(foirequest):
    return Report.objects.filter(foirequest=foirequest).count()
