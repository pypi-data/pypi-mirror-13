import re
import six

from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.forms.widgets import TextInput

from django.db.models import SlugField
from django.template.defaultfilters import slugify
from django_hstore.widgets import BaseAdminHStoreWidget
from django_hstore.forms import JsonMixin

try:
    from django.utils.timezone import now as datetime_now
    assert datetime_now
except ImportError:
    import datetime
    datetime_now = datetime.datetime.now

try:
    from django.utils.encoding import force_unicode  # NOQA
except ImportError:
    from django.utils.encoding import force_text as force_unicode  # NOQA


MAX_UNIQUE_QUERY_ATTEMPTS = 100


class UniqueFieldMixin(object):

    def check_is_bool(self, attrname):
        if not isinstance(getattr(self, attrname), bool):
            raise ValueError("'{}' argument must be True or False".format(attrname))

    def get_queryset(self, model_cls, slug_field):
        for field, model in model_cls._meta.get_fields_with_model():
            if model and field == slug_field:
                return model._default_manager.all()
        return model_cls._default_manager.all()

    def find_unique(self, model_instance, field, iterator, *args):
        # exclude the current model instance from the queryset used in finding
        # next valid hash
        queryset = self.get_queryset(model_instance.__class__, field)
        if model_instance.pk:
            queryset = queryset.exclude(pk=model_instance.pk)

        # form a kwarg dict used to impliment any unique_together contraints
        kwargs = {}
        for params in model_instance._meta.unique_together:
            if self.attname in params:
                for param in params:
                    kwargs[param] = getattr(model_instance, param, None)

        new = six.next(iterator)
        kwargs[self.attname] = new
        while not new or queryset.filter(**kwargs):
            new = six.next(iterator)
            kwargs[self.attname] = new
        setattr(model_instance, self.attname, new)
        return new


class AutoSlugField(UniqueFieldMixin, SlugField):
    """ AutoSlugField
    By default, sets editable=False, blank=True.
    Required arguments:
    populate_from
        Specifies which field or list of fields the slug is populated from.
    Optional arguments:
    separator
        Defines the used separator (default: '-')
    overwrite
        If set to True, overwrites the slug on every save (default: False)
    Inspired by SmileyChris' Unique Slugify snippet:
    http://www.djangosnippets.org/snippets/690/
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('blank', True)
        kwargs.setdefault('editable', False)

        populate_from = kwargs.pop('populate_from', None)
        if populate_from is None:
            raise ValueError("missing 'populate_from' argument")
        else:
            self._populate_from = populate_from

        self.slugify_function = kwargs.pop('slugify_function', slugify)
        self.separator = kwargs.pop('separator', six.u('-'))
        self.overwrite = kwargs.pop('overwrite', False)
        self.check_is_bool('overwrite')
        self.allow_duplicates = kwargs.pop('allow_duplicates', False)
        self.check_is_bool('allow_duplicates')
        super(AutoSlugField, self).__init__(*args, **kwargs)

    def _slug_strip(self, value):
        """
        Cleans up a slug by removing slug separator characters that occur at
        the beginning or end of a slug.
        If an alternate separator is used, it will also replace any instances
        of the default '-' separator with the new separator.
        """
        re_sep = '(?:-|%s)' % re.escape(self.separator)
        value = re.sub('%s+' % re_sep, self.separator, value)
        return re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)

    def slugify_func(self, content):
        if content:
            return self.slugify_function(content)
        return ''

    def slug_generator(self, original_slug, start):
        yield original_slug
        for i in range(start, MAX_UNIQUE_QUERY_ATTEMPTS):
            slug = original_slug
            end = '%s%s' % (self.separator, i)
            end_len = len(end)
            if self.slug_len and len(slug) + end_len > self.slug_len:
                slug = slug[:self.slug_len - end_len]
                slug = self._slug_strip(slug)
            slug = '%s%s' % (slug, end)
            yield slug
        raise RuntimeError('max slug attempts for %s exceeded (%s)' %
            (original_slug, MAX_UNIQUE_QUERY_ATTEMPTS))

    def create_slug(self, model_instance, add):
        # get fields to populate from and slug field to set
        if not isinstance(self._populate_from, (list, tuple)):
            self._populate_from = (self._populate_from, )
        slug_field = model_instance._meta.get_field(self.attname)

        if add or self.overwrite:
            # slugify the original field content and set next step to 2
            slug_for_field = lambda field: self.slugify_func(getattr(model_instance, field))
            slug = self.separator.join(map(slug_for_field, self._populate_from))
            start = 2
        else:
            # get slug from the current model instance
            slug = getattr(model_instance, self.attname)
            # model_instance is being modified, and overwrite is False,
            # so instead of doing anything, just return the current slug
            return slug

        # strip slug depending on max_length attribute of the slug field
        # and clean-up
        self.slug_len = slug_field.max_length
        if self.slug_len:
            slug = slug[:self.slug_len]
        slug = self._slug_strip(slug)
        original_slug = slug

        if self.allow_duplicates:
            return slug

        return super(AutoSlugField, self).find_unique(
            model_instance, slug_field, self.slug_generator(original_slug, start))

    def pre_save(self, model_instance, add):
        value = force_unicode(self.create_slug(model_instance, add))
        return value

    def get_internal_type(self):
        return "SlugField"

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = '%s.AutoSlugField' % self.__module__
        args, kwargs = introspector(self)
        kwargs.update({
            'populate_from': repr(self._populate_from),
            'separator': repr(self.separator),
            'overwrite': repr(self.overwrite),
            'allow_duplicates': repr(self.allow_duplicates),
        })
        # That's our definition!
        return (field_class, args, kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(AutoSlugField, self).deconstruct()
        kwargs['populate_from'] = self._populate_from
        if not self.separator == six.u('-'):
            kwargs['separator'] = self.separator
        if self.overwrite is not False:
            kwargs['overwrite'] = True
        if self.allow_duplicates is not False:
            kwargs['allow_duplicates'] = True
        return name, path, args, kwargs


class SliderWidget(forms.TextInput):
    """
    Creates a single slider and returns the value selected
    """
    def __init__(self, min_value, max_value, attrs=None):
        super(SliderWidget, self).__init__(attrs)
        self.min_value = min_value
        self.max_value = max_value
        self.slider_type = "single"
        self.grid = "1"

    def to_python(self, value):
        "Returns a Unicode object."
        if value in self.empty_values:
            return ''

    def _get_attrs(self, value, attrs=None):
        attrs = attrs or {}
        attrs["data-type"] = self.slider_type
        attrs["data-min"] = str(self.min_value)
        attrs["data-max"] = str(self.max_value)
        attrs["data-grid"] = self.grid
        return attrs

    def _get_value(self, value):
        """
        Make any chagnes to the value and return it
        """
        return value

    def render(self, name, value, attrs=None):
        value = self._get_value(value)
        attrs = self._get_attrs(value, attrs)

        html = super(SliderWidget, self).render(name, value, attrs)
        if '__prefix__' not in attrs['id']:
            more_html = [
                "<script>",
                '$("#%s").ionRangeSlider();' % attrs['id'],
                "</script>"
            ]
            addl_html = "".join(more_html)
            html = mark_safe(html + addl_html)
        return html

    class Media:
        css = {
            'screen': ('eventcalendar/ion.rangeSlider.css', )
        }
        js = ('eventcalendar/ion.rangeSlider.js', )


class RangeWidget(SliderWidget):
    """
    A double sided-slider
    """
    def __init__(self, min_value, max_value, attrs=None):
        super(RangeWidget, self).__init__(min_value, max_value, attrs)
        self.slider_type = "double"

    def to_python(self, value):
        "Returns a Unicode object."
        if value in self.empty_values:
            return ''
        return value.split(";")

    def _get_attrs(self, value, attrs=None):
        attrs = super(RangeWidget, self)._get_attrs(value, attrs)
        attrs["data-from"] = value[0]
        attrs["data-to"] = value[1]
        return attrs

    def _get_value(self, value):
        return value or [value[0], value[1]]


class RangeField(forms.MultiValueField):
    """
    price_range = RangeField(forms.IntegerField, widget=MyWidget)
    """
    default_error_messages = {
        'invalid_start': _(u'Enter a valid start value.'),
        'invalid_end': _(u'Enter a valid end value.'),
    }
    default_min = 0
    default_max = 10
    widget_class = RangeWidget

    def __init__(self, field_class, min_value=None, max_value=None, *args, **kwargs):
        self.min_value = min_value or self.default_min
        self.max_value = max_value or self.default_max

        if 'initial' not in kwargs:
            kwargs['initial'] = [self.min_value, self.max_value]

        self.fields = (field_class(), field_class())

        super(RangeField, self).__init__(
            fields=self.fields,
            widget=self.widget_class(self.min_value, self.max_value), *args, **kwargs
        )

    def clean(self, value):
        value = value.split(";")
        return super(RangeField, self).clean(value)

    def compress(self, data_list):
        if data_list:
            return [
                self.fields[0].clean(data_list[0]),
                self.fields[1].clean(data_list[1])
            ]

        return None


class FrontEndHStoreWidget(JsonMixin, BaseAdminHStoreWidget):
    admin_style = 'frontend'

    @property
    def media(self):
        js = [
            "admin/js/django_hstore/underscore-min.js",
            "eventcalendar/hstore-widget.js"
        ]
        return forms.Media(js=js)


class ClearableWidget(TextInput):
    def render(self, name, value, attrs=None):
        from django.forms.utils import flatatt
        from django.utils.html import format_html
        from django.utils.encoding import force_text

        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self._format_value(value))
        return format_html('<div class="ng-form-icon-right ng-width-1-1"><a class="ng-close ng-hidden"></a><input{} /></div>', flatatt(final_attrs))
