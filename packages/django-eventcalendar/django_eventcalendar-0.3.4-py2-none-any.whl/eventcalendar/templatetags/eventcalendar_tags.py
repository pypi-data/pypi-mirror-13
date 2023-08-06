# -*- coding: utf-8 -*-
import re
from django.utils.safestring import mark_safe
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()
class_re = re.compile(r'(?<=class=["\'])(.*?)(?=["\'])')


@register.filter
def add_class(value, css_class):
    string = unicode(value)
    match = class_re.search(string)
    if match:
        m = re.search(r'^%s$|^%s\s|\s%s\s|\s%s$' % (css_class, css_class,
                                                    css_class, css_class), match.group(1))
        if not m:
            return mark_safe(class_re.sub(match.group(1) + " " + css_class,
                                          string))
    else:
        return mark_safe(string.replace('>', ' class="%s">' % css_class))
    return value


@register.filter
@stringfilter
def replace(value, arg):
    """
    Replace a string in a string
    """
    args = arg.split("|")
    if len(args) >= 2:
        return value.replace(args[0], args[1])
    elif len(args) == 1:
        return value.replace(args[0], "")
    return value
