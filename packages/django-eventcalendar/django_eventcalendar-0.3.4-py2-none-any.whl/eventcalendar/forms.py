"""
Convenience forms for adding and updating ``Event`` and ``Occurrence``s.

"""
from __future__ import print_function, unicode_literals
from datetime import datetime
from django import VERSION
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.forms.utils import to_current_timezone

from django_hstore.forms import DictionaryField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML
from haystack.forms import FacetedSearchForm

from .settings import TIMESLOT_INTERVAL, DEFAULT_OCCURRENCE_DURATION
from .models import Event, Schedule, Venue
from .fields import SliderWidget, RangeField, FrontEndHStoreWidget, ClearableWidget
import utils

FIELDS_REQUIRED = (VERSION[:2] >= (1, 6))
MINUTES_INTERVAL = TIMESLOT_INTERVAL.seconds // 60
SECONDS_INTERVAL = utils.time_delta_total_seconds(DEFAULT_OCCURRENCE_DURATION)


class CustomSplitDateTimeWidget(forms.MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """
    supports_microseconds = False

    def __init__(self, attrs=None, date_format=None, time_format=None):
        date_attrs = attrs or {}
        time_attrs = attrs or {}
        date_attrs['type'] = 'date'
        time_attrs['type'] = 'time'

        widgets = (forms.DateInput(attrs=date_attrs, format=date_format),
                   forms.TimeInput(attrs=time_attrs, format=time_format))
        super(CustomSplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]


class MultipleIntegerField(forms.MultipleChoiceField):
    """
    A form field for handling multiple integers.

    """
    def __init__(self, choices, size=None, label=None, widget=None):
        if widget is None:
            widget = forms.SelectMultiple(attrs={'size': size or len(choices)})
        super(MultipleIntegerField, self).__init__(
            required=False,
            choices=choices,
            label=label,
            widget=widget,
        )

    def clean(self, value):
        return [int(i) for i in super(MultipleIntegerField, self).clean(value)]


class ScheduleFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ScheduleFormHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_tag = False
        self.layout = Layout(
            Fieldset(
                'Date and Time Information',
                'begins',
                'duration',
            ),
            Fieldset(
                'Recurring Options',
                'schedule_text',
                'rrule_str',
                HTML("""<p>Examples:</p><ul class="ng-list ng-list-bullet">
            <li>Every weekday</li>
            <li>Every 2 weeks on Tuesday</li>
            <li>Every week on Monday, Wednesday</li>
            <li>Every month on the 2nd last Friday for 7 times</li>
            <li>Every 6 months</li></ul>""")
            ),
        )


class ScheduleForm(forms.ModelForm):
    """
    Schedule Form with just a text field
    """
    begins = forms.SplitDateTimeField(
        label=_('Begins'),
        widget=CustomSplitDateTimeWidget(),
        initial=datetime.now,
    )
    duration = forms.DecimalField(
        label=_("Duration in hours"),
        widget=SliderWidget(
            min_value=0,
            max_value=24,
            attrs={
                'data-step': '0.5',
                'data-grid-num': '6',
            }),
        initial=1
    )
    schedule_text = forms.CharField(
        label="Type in the recurring schedule",
        widget=forms.TextInput(),
        required=False)
    rrule_str = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)

    class Meta:
        model = Schedule
        fields = '__all__'

    class Media:
        js = ('eventcalendar/rrule.js', 'eventcalendar/nlp.js', )


class EventForm(forms.ModelForm):
    """
    A simple form for adding and updating Event attributes
    """
    required_css_class = "ng-form-required"
    error_css_class = "ng-form-danger"
    min_age = forms.IntegerField(widget=forms.HiddenInput(), required=False, initial=0)
    max_age = forms.IntegerField(widget=forms.HiddenInput(), required=False, initial=100)
    age_range = RangeField(forms.IntegerField, min_value=0, max_value=100, required=False)
    price_info = DictionaryField(widget=FrontEndHStoreWidget, required=False)
    location_name = forms.CharField(required=False, widget=ClearableWidget(attrs={'class': "textinput textInput ng-width-1-1"}))
    raw_location = forms.CharField(label="Location address", required=True)
    venue = forms.ModelChoiceField(
        queryset=Venue.objects.all(),
        widget=forms.HiddenInput,
        required=False)

    class Meta:
        model = Event
        fields = (
            "title", "category", "description", "location_name", "raw_location",
            "venue", "image",
            "age_range", "more_info_url", "tickets_url", "price_info",
            "min_age", "max_age")

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs and kwargs['instance']:
            kwargs['initial']['age_range'] = "%s;%s" % (kwargs['instance'].min_age, kwargs['instance'].max_age, )
        super(EventForm, self).__init__(*args, **kwargs)
        self.form_helper = FormHelper()
        self.form_helper.form_tag = False
        self.form_helper.layout = Layout(
            Fieldset(
                'Event Information',
                'title',
                'category',
                'description'),
            Fieldset(
                'Location Information',
                'location_name',
                'raw_location',
                'venue'),
            Fieldset(
                'Additional Information',
                'more_info_url',
                'tickets_url',
                'price_info',
                'age_range',
                'image',
                'min_age',
                'max_age',
            )
        )

    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        title = cleaned_data.get('title', '')
        cleaned_data['slug'] = slugify(title)
        return cleaned_data


class OccurrenceSearchForm(FacetedSearchForm):
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    address = forms.CharField(required=False)
    distance = forms.ChoiceField(
        choices=(
            ('5', '5 miles'),
            ('10', '10 miles'),
            ('25', '25 miles'),
            ('50', '50 miles'),
        ),
        initial='5',
        required=False
    )
    use_current_location = forms.BooleanField(required=False, initial=False)
    latitude = forms.CharField(required=False, widget=forms.HiddenInput)
    longitude = forms.CharField(required=False, widget=forms.HiddenInput)
    neighborhoods = forms.MultipleChoiceField(
        required=False,
        choices=()
    )
    categories = forms.MultipleChoiceField(
        required=False,
        choices=()
    )
    # sorting = forms.ChoiceField(
    #     choices=(
    #         ('start_time', 'Date'),
    #         ('proximity', 'Proximity'),
    #         ('-score', 'Relevance'), ),
    #     initial='start_time',
    #     required=False,
    #     widget=forms.HiddenInput
    # )

    def __init__(self, *args, **kwargs):
        super(OccurrenceSearchForm, self).__init__(*args, **kwargs)

        # Setup dynamic choices
        from .models import Neighborhood, EventCategory
        from django.core.cache import caches
        cache = caches['default']
        neighborhoods = cache.get('eventcalendar_neighborhoods')
        if not neighborhoods:
            neighborhoods = list(Neighborhood.objects.values_list('slug', 'name'))
            cache.set('eventcalendar_neighborhoods', neighborhoods, 3600)
        categories = cache.get('eventcalendar_categories')
        if not categories:
            categories = list(EventCategory.objects.values_list('slug', 'name'))
            cache.set('eventcalendar_neighborhoods', categories, 3600)
        self.fields['neighborhoods'].choices = neighborhoods
        self.fields['categories'].choices = categories

        # Set up faceting
        self.searchqueryset = self.searchqueryset.order_by('start_time')
        self.searchqueryset = self.searchqueryset.facet('neighborhood')
        self.searchqueryset = self.searchqueryset.facet('category')
        self.location = None

    def no_query_found(self):
        """
        Determines the behavior when no query was found.

        By default, no results are returned (``EmptySearchQuerySet``).

        Should you want to show all results, override this method in your
        own ``SearchForm`` subclass and do ``return self.searchqueryset.all()``.
        """
        return self.searchqueryset.all()

    def geocode(self):
        """
        Process the form for geocoding.

        If the latitude and longitude are already set, then we're done. Otherwise
        see if the address field is set and geocodable.

        Returns nothing, but sets the latitude and longitude cleaned_data
        """
        from .utils import geocodable, geocode
        from haystack.utils.geo import Point
        if 'latitude' not in self.cleaned_data:
            return
        if 'longitude' not in self.cleaned_data:
            return

        try:
            self.cleaned_data['latitude'] = float(self.cleaned_data['latitude'])
            self.cleaned_data['longitude'] = float(self.cleaned_data['longitude'])
            if self.cleaned_data['latitude'] and self.cleaned_data['longitude']:
                self.location = Point(self.cleaned_data['longitude'], self.cleaned_data['latitude'])
                return
        except ValueError:
            self.cleaned_data['latitude'] = ''
            self.cleaned_data['longitude'] = ''
            return

        if geocodable(self.cleaned_data.get('address', '')):
            loc = geocode(self.cleaned_data['address'])
            if loc:
                self.location = Point(loc.longitude, loc.latitude)

    def search(self):
        from elasticsearch_dsl.query import Q
        from elasticsearch_dsl.filter import F
        from search_indexes import OccurrenceDoc
        from haystack import connections as haystack_connections
        from elasticsearch_dsl.connections import connections

        self.geocode()

        backend = haystack_connections['eventcalendar'].get_backend()
        connections.add_connection('default', backend.conn)
        search_query = OccurrenceDoc.search(using='default', index=backend.index_name)
        # search_query.doc_type(OccurrenceDoc)

        if self.cleaned_data['q']:
            text_query = Q({
                "multi_match": {
                    "query": self.cleaned_data['q'],
                    "type": "best_fields",
                    "fields": ["text", "title", "description", "neighborhood", "venue"]
                }
            })
        else:
            text_query = Q({"match_all": {}})

        search_query = search_query.query(text_query)

        if self.cleaned_data['neighborhoods']:
            if len(self.cleaned_data['neighborhoods']) > 1:
                f = F({'terms': {'neighborhood_exact': self.cleaned_data['neighborhoods']}})
            else:
                f = F({'term': {'neighborhood_exact': self.cleaned_data['neighborhoods'][0]}})
            search_query = search_query.filter(f)

        if self.cleaned_data['categories']:
            if len(self.cleaned_data['categories']) > 1:
                f = F({'terms': {'category_exact': self.cleaned_data['categories']}})
            else:
                f = F({'term': {'category_exact': self.cleaned_data['categories'][0]}})
            search_query = search_query.filter(f)

        f = {'range': {'start_time': {'gte': 'now'}}}
        if self.cleaned_data['end_date']:
            f['range']['start_time']['lte'] = self.cleaned_data['end_date'].isoformat() + "||/d"
        search_query = search_query.filter(F(f))

        if self.location:
            try:
                dist = int(self.cleaned_data.get('distance', 5))
            except ValueError:
                dist = 5
            f = F({
                "geo_distance": {
                    "distance": "%smi" % dist,
                    "pin.location": {
                        "lat": self.location.y,
                        "lon": self.location.x
                    }
                }
            })
            search_query = search_query.filter(f)

        search_query.aggs.bucket('by_date', 'date_histogram', field='start_time', interval='day', format="yyyy-MM-dd")
        search_query.aggs.bucket('by_neighborhood', 'terms', field='neighborhood')
        search_query.aggs.bucket('by_category', 'terms', field='category')
        search_query = search_query.sort('start_time')
        return search_query
