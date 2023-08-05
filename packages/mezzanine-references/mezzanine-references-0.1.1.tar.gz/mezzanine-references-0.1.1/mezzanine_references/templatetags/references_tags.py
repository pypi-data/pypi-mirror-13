# -*- coding: utf-8 -*-

from django import template
from mezzanine.conf import settings
from mezzanine_references.models import References

register = template.Library()


@register.inclusion_tag('references/slideshow.html')
def references_slideshow(**kwargs):
    page = References.objects.get(**kwargs)
    return {
        'references_page': page,
        'references': page.reference_set.all(),
        'MEDIA_URL': settings.MEDIA_URL,
    }
