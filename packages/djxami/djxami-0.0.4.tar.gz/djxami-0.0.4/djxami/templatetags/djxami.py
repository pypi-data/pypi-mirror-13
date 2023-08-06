from django.shortcuts import render_to_response
from django.template import Library
from django.conf import settings
from django.utils.safestring import mark_safe

register = Library()


@register.inclusion_tag('djxami/init.html')
def djxami_init():
    return {
        'first_query_pause': getattr(settings, 'DJXAMI_FIRST_QUERY_PAUSE', 1000),
        'queries_interval': getattr(settings, 'DJXAMI_QUERIES_INTERVAL', 5000),
        'stream_interval': getattr(settings, 'DJXAMI_STREAM_INVETRAL', 1000),
    }
