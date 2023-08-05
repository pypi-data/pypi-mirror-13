# -*- coding: utf-8 -*-

from django import template
from mezzanine.conf import settings
from mezzanine_faq.models import FaqPage

register = template.Library()


@register.inclusion_tag('includes/faqlist.html')
def faq_list(**kwargs):
    page = FaqPage.objects.get(**kwargs)
    return {
        'page': page,
        'faq_questions': page.faqquestion_set.all(),
        'MEDIA_URL': settings.MEDIA_URL,
    }


@register.inclusion_tag('includes/faqlist.html')
def faq_last(**kwargs):
    page = FaqPage.objects.get(**kwargs)
    return {
        'page': page,
        'faq_questions': page.faqquestion_set.all().order_by('-id')[:1],
        'MEDIA_URL': settings.MEDIA_URL,
    }
