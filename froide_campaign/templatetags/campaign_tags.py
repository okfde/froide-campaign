import base64
import hashlib

from django import template
from django.conf import settings
from django.utils.html import mark_safe
from django.contrib.staticfiles import finders
from django.templatetags.static import static


register = template.Library()


def sha384(filepath):
    sha = hashlib.sha384()
    with open(filepath, 'rb') as f:
        while True:
            block = f.read(1024)
            if not block:
                break
            sha.update(block)
        return sha.digest()


def subresource_integrity(filepath):
    sha = sha384(filepath)
    return 'sha384-' + base64.b64encode(sha).decode('utf-8')


@register.simple_tag
def output_static(path):
    result = finders.find(path)
    with open(result) as f:
        return mark_safe(f.read())


@register.simple_tag
def script_tag(path):
    url = settings.SITE_URL + static(path)
    filepath = finders.find(path)
    sri = subresource_integrity(filepath)
    return mark_safe(
        '<script src="{url}" integrity="{sri}" crossorigin="anonymous" '
        'async></script>'.format(url=url, sri=sri)
    )
