# coding: utf-8

from __future__ import print_function, unicode_literals

from django import template

from cmstemplates import queries as q


register = template.Library()


@register.simple_tag(takes_context=True)
def cms_group(context, name, description=''):
    template_group = q.get_template_group(name, description)
    content = q.get_cached_content_for_group(template_group)
    return template.Template(content).render(context)
