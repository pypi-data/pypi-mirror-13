import re
from datetime import datetime, timedelta
from dateutil import rrule

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse

from .settings import STORAGE_CLASS, CATEGORY_TYPE_CHOICES, DEFAULT_ORIGIN
from .fields import AutoSlugField
from .utils import fit_to_box, fill_box, generate_url
from django_hstore import hstore
from ckeditor.fields import RichTextField


class ImageObject(object):
    ACCESSOR_MAPPINGS = (
        (re.compile('get_([0-9]+x[0-9]+)_url'), '_get_SIZE_url'),
        (re.compile('get_(.*)_size'), '_get_SIZE_size')
    )

    def smart_fit(self, width=20000, height=20000):
        """
        Given a width, height or both, it will return the width and height to
        fit in the given area.
        """
        return fit_to_box((self.image_width, self.image_height), width, height)

    def smart_fill(self, width, height):
        """
        Fill the image to the given width and height
        """
        orig_dims = (self.image_width, self.image_height)
        dest_dims = (width, height)
        return fill_box(orig_dims, dest_dims)

    def _get_SIZE_size(self, size):  # NOQA
        width, height = map(int, size.split('x'))
        return self.smart_fit(width, height)

    def _get_SIZE_url(self, size):  # NOQA
        """
        Return the URL for the given size (dddxddd)
        """
        width, height = map(int, size.split('x'))
        if self.image_width is None or self.image_height is None:
            return ''
        crop_dims = self.smart_fill(width, height)
        if crop_dims == (0, 0, self.image_width, self.image_height) or crop_dims is None:
            processors = ["_r%dx%d" % (width, height), ]
        else:
            processors = [
                '_c%d-%d-%d-%d' % crop_dims,
                "_r%dx%d" % (width, height),
            ]
        return generate_url(self.image.url, "".join(processors))

    def get_size(self, size):
        if 'x' in size:
            func_name = "get_%s_size" % size
            func = getattr(self, func_name, lambda: None)
            return func()

        return None

    def get_url(self, size):
        if 'x' in size:
            func_name = "get_%s_url" % size
            func = getattr(self, func_name, lambda: '')
            return func()

        return ''

    def get_purge_url(self):
        from hashlib import sha1
        from django.conf import settings
        transmogrify_key = getattr(settings, 'TRANSMOGRIFY_SECRET_KEY', settings.SECRET_KEY)
        security_hash = sha1('PURGE' + transmogrify_key).hexdigest()
        return "%s?%s" % (self.image.url, security_hash)

    @property
    def ratio(self):
        return ((self.image_width * 1.0) / self.image_height) * 1000

    def __getattr__(self, name):
        """
        Delegate to size accessor methods if it is such a call
        """
        from django.utils.functional import curry

        method_name = name
        for reg, fnct_name in self.ACCESSOR_MAPPINGS:
            m = reg.match(method_name)
            if m:
                groups = m.groups()
                size = groups[0]
                if not size:
                    size = groups[-1]
                fnct = getattr(self, fnct_name)
                return curry(fnct, size)
        raise AttributeError('No method %s' % method_name)


@python_2_unicode_compatible
class EventCategory(models.Model):
    """
    Simple ``Event`` classifcation.
    """
    name = models.CharField(_('name'), max_length=50)
    slug = models.SlugField(_('slug'), max_length=50)
    event_type = models.CharField(
        _('event type'),
        max_length=50,
        choices=CATEGORY_TYPE_CHOICES,
        default="Event",
        help_text="Used in microformats to better indicate the type of event.")

    class Meta:
        verbose_name = _('event type')
        verbose_name_plural = _('event types')
        ordering = ('name', )

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Neighborhood(models.Model):
    """
    Towns or Neighborhoods
    """
    name = models.CharField(_('name'), max_length=255)
    slug = AutoSlugField(_('slug'), populate_from='name', max_length=255)
    geography = models.MultiPolygonField()

    objects = models.GeoManager()

    class Meta:
        verbose_name = _('neighborhood')
        verbose_name_plural = _('neighborhoods')
        ordering = ('name', )

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class VenueCategory(models.Model):
    """
    Simple ``Venue`` classifcation.
    """
    name = models.CharField(_('name'), max_length=50)
    slug = models.SlugField(_('slug'), max_length=50)

    class Meta:
        verbose_name = _('venue type')
        verbose_name_plural = _('venue types')
        ordering = ('name', )

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Venue(models.Model, ImageObject):
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255)
    venue_type = models.ForeignKey(
        VenueCategory,
        verbose_name=_('venue type'),
        blank=True, null=True)
    address = models.CharField(
        _('address'),
        max_length=255)
    neighborhood = models.ForeignKey(
        Neighborhood,
        verbose_name=_('neighborhood'),
        null=True, blank=True)
    phone = models.CharField(
        _('phone'),
        max_length=25,
        blank=True, null=True)
    website = models.URLField(
        _('web site'),
        max_length=255,
        blank=True, null=True)
    latlong = models.PointField(
        _('latitude-longitude'),
        blank=True, null=True)
    image = models.FileField(
        _('image'),
        storage=STORAGE_CLASS(),
        blank=True, null=True,
        max_length=255)
    image_width = models.PositiveIntegerField(
        _('image width'),
        blank=True, null=True)
    image_height = models.PositiveIntegerField(
        _('image height'),
        blank=True, null=True)
    description = RichTextField(
        _('description'),
        blank=True, null=True,
        config_name="eventcalendar-editor")
    special_instructions = RichTextField(
        _('special instructions'),
        blank=True, null=True,
        config_name="eventcalendar-editor")

    objects = models.GeoManager()

    class Meta:
        verbose_name = "Venue"
        verbose_name_plural = "Venues"
        ordering = ('name', )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        geocode and update neighborhood if not set
        """
        from .utils import geocode
        if not self.latlong and self.parsable_address:
            self.latlong = geocode(self.address)
        if self.latlong and not self.neighborhood:
            n = Neighborhood.objects.filter(geography__contains=self.latlong)
            if n:
                self.neighborhood = n[0]
        super(Venue, self).save(*args, **kwargs)

    def _setup_parsed_address(self):
        from .utils import parse_address
        if self.address:
            address, address_type = parse_address(self.address)
            self._parsed_address = address
            self._parsable_address = (address_type not in ('PO Box', 'Ambiguous', 'BadAddress'))
        else:
            self._parsed_address = ''
            self._parsable_address = False

    @property
    def parsed_address(self):
        if not hasattr(self, '_parsed_address'):
            self._setup_parsed_address()
        return self._parsed_address

    @property
    def parsable_address(self):
        if not hasattr(self, '_parsable_address'):
            self._setup_parsed_address()
        return self._parsable_address


@python_2_unicode_compatible
class Event(models.Model, ImageObject):
    """
    Container model for general metadata and associated ``Occurrence`` entries.
    """
    title = models.CharField(_('name of event'), max_length=255)
    slug = AutoSlugField(_('slug'), populate_from='title', max_length=255)
    description = RichTextField(
        _('description'),
        blank=True,
        default="",
        config_name='eventcalendar-editor')
    category = models.ForeignKey(
        EventCategory,
        verbose_name=_('category'))
    location_name = models.CharField(
        _('location name'),
        max_length=255,
        blank=True, null=True)
    raw_location = models.CharField(
        _('location address'),
        max_length=255,
        blank=True, null=True)
    neighborhood = models.ForeignKey(
        Neighborhood,
        verbose_name=_('neighborhood'),
        null=True, blank=True)
    latlong = models.PointField(
        _('latitude-longitude'),
        blank=True, null=True)
    venue = models.ForeignKey(
        Venue,
        verbose_name=_('venue'),
        blank=True, null=True)
    min_age = models.PositiveIntegerField(
        _('minimum age'),
        blank=True, null=True,
        default=0)
    max_age = models.PositiveIntegerField(
        _('maximum age'),
        blank=True, null=True,
        default=100)
    more_info_url = models.URLField(
        _('URL for more info'),
        blank=True, null=True)
    more_info_phone = models.CharField(
        _('Phone for more info'),
        max_length=50,
        blank=True, null=True)
    tickets_url = models.URLField(
        _('URL for tickets'),
        blank=True, null=True)
    image = models.FileField(
        _('event image'),
        blank=True, null=True,
        max_length=255)
    image_width = models.PositiveIntegerField(
        _('image width'),
        blank=True, null=True)
    image_height = models.PositiveIntegerField(
        _('image height'),
        blank=True, null=True)
    price_info = hstore.DictionaryField(
        verbose_name=_('price info'),
        blank=True, null=True)
    submitter = models.ForeignKey('auth.User')
    origin = models.CharField(
        _("origin"),
        max_length=255,
        blank=True, null=True,
        help_text="The source domain for that originated this event submission")
    approved = models.BooleanField(
        _('approved'),
        default=False)
    external_id = models.CharField(_('external ID'), max_length=50, blank=True, null=True)

    objects = hstore.HStoreManager()

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('title', )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        geocode and update neighborhood if not set
        """
        from .utils import geocode
        if self.venue:
            self.latlong = self.venue.latlong
            self.neighborhood = self.venue.neighborhood
        if not self.latlong and self.parsable_address:
            self.latlong = geocode(self.raw_location)
        if self.latlong and not self.neighborhood:
            n = Neighborhood.objects.filter(geography__contains=self.latlong)
            if n:
                self.neighborhood = n[0]
        if not self.origin:
            self.origin = DEFAULT_ORIGIN
        super(Event, self).save(*args, **kwargs)

    @property
    def age_range(self):
        if self.min_age == 0:
            if self.max_age == 100:
                return "All ages"
            else:
                return "%d and under" % self.max_age
        else:
            if self.max_age == 100:
                return "%d and up" % self.min_age
            else:
                return "%d - %d" % (self.min_age, self.max_age)

    def _setup_parsed_address(self):
        from .utils import parse_address
        if self.venue:
            self._parsed_address = self.venue.parsed_address
            self._parsable_address = self.venue.parsable_address
        elif self.raw_location:
            address, address_type = parse_address(self.raw_location)
            self._parsed_address = address
            self._parsable_address = (address_type not in ('PO Box', 'Ambiguous', 'BadAddress'))
        else:
            self._parsed_address = ''
            self._parsable_address = False

    @property
    def parsed_address(self):
        if not hasattr(self, '_parsed_address'):
            self._setup_parsed_address()
        return self._parsed_address

    @property
    def parsable_address(self):
        if not hasattr(self, '_parsable_address'):
            self._setup_parsed_address()
        return self._parsable_address

    @property
    def location_street(self):
        return self.parsed_address['street']

    @property
    def location_city(self):
        print self.parsed_address
        return self.parsed_address['city']

    @property
    def location_state(self):
        return self.parsed_address['state']

    @property
    def location_zip(self):
        return self.parsed_address['zipcode']

    def get_absolute_url(self):
        return reverse('eventcalendar-event', args=(), kwargs={"slug": self.slug})

    def add_schedule(self, start_time, duration, **rrule_params):
        """
        Add one or more occurrences to the event using a comparable API to
        ``dateutil.rrule``.

        If ``rrule_params`` does not contain a ``freq``, one will be defaulted
        to ``rrule.DAILY``.

        Because ``rrule.rrule`` returns an iterator that can essentially be
        unbounded, we need to slightly alter the expected behavior here in order
        to enforce a finite number of occurrence creation.

        If both ``count`` and ``until`` entries are missing from ``rrule_params``,
        only a single ``Occurrence`` instance will be created using the exact
        ``start_time`` and ``end_time`` values.
        """
        count = rrule_params.get('count')
        until = rrule_params.get('until')
        if not (count or until):
            self.occurrence_set.create(start_time=start_time, duration=duration)
        else:
            rrule_params.setdefault('freq', rrule.DAILY)
            end_time = start_time + datetime.timedelta(hours=duration)
            occurrences = []
            for ev in rrule.rrule(dtstart=start_time, **rrule_params):
                occurrences.append(Occurrence(start_time=ev, end_time=end_time, event=self))
            self.occurrence_set.bulk_create(occurrences)

    def upcoming_occurrences(self):
        """
        Return all occurrences that are set to start on or after the current
        time.
        """
        return self.occurrence_set.filter(start_time__gte=datetime.now())

    def next_occurrence(self):
        """
        Return the single occurrence set to start on or after the current time
        if available, otherwise ``None``.
        """
        upcoming = self.upcoming_occurrences()
        return upcoming[0] if upcoming else None

    def daily_occurrences(self, dt=None):
        """
        Convenience method wrapping ``Occurrence.objects.daily_occurrences``.
        """
        return Occurrence.objects.daily_occurrences(dt=dt, event=self)


@python_2_unicode_compatible
class Schedule(models.Model):
    """
    Represents a single or recurring schedule for an event
    """
    event = models.ForeignKey(
        Event,
        related_name="schedules",
        verbose_name=_('event'))
    begins = models.DateTimeField(
        _('begins'),
        default=timezone.now)
    duration = models.DecimalField(
        _('duration'),
        max_digits=4,
        decimal_places=2,
        default=1.0)
    schedule_text = models.TextField(_('schedule text'), blank=True, null=True)
    rrule_str = models.TextField(_('recurring rule'), blank=True, null=True)

    @property
    def rrule(self):
        rule = getattr(self, "_rrule", None)
        if rule:
            return rule
        try:
            self._rrule = rrule.rrulestr(self.rrule_str)
        except Exception:
            return None
        return self._rrule

    @property
    def _dates(self):
        """
        Determine the datetimes based on the start date and recurring rule
        """
        if self.rrule:
            return list(self.rrule)
        else:
            return [self.begins]

    def syncronize_occurrences(self):
        """
        Make sure all occurrences tied to the schedule are valid and add any missing
        """
        # Make sure existing occurrences are in dates
        self.occurrences.all().delete()
        for d in self._dates:
            end_date = self.begins + timedelta(hours=float(self.duration))
            if hasattr(self.begins, 'tzinfo'):
                end_date.replace(tzinfo=self.begins.tzinfo)
            self.occurrences.create(
                event=self.event,
                start_time=self.begins,
                end_time=end_date)

    def save(self, *args, **kwargs):
        if self.rrule_str:
            rule = self.rrule
            if rule is None:
                self.rrule_str = ""
        super(Schedule, self).save(*args, **kwargs)
        self.syncronize_occurrences()

    def __str__(self):
        out = 'DTSTART: %s' % self.begins.isoformat()
        if self.rrule_str:
            return out + self.rrule_str
        else:
            return out


class OccurrenceManager(hstore.HStoreManager):

    use_for_related_fields = True

    def daily_occurrences(self, dt=None, event=None):
        """
        Returns a queryset of for instances that have any overlap with a
        particular day.

        * ``dt`` may be either a datetime.datetime, datetime.date object, or
          ``None``. If ``None``, default to the current day.

        * ``event`` can be an ``Event`` instance for further filtering.
        """
        dt = dt or datetime.now()
        start = datetime(dt.year, dt.month, dt.day)
        end = start.replace(hour=23, minute=59, second=59)
        qs = self.filter(
            models.Q(
                start_time__gte=start,
                start_time__lte=end,
            ) |
            models.Q(
                end_time__gte=start,
                end_time__lte=end,
            ) |
            models.Q(
                start_time__lt=start,
                end_time__gt=end
            )
        )

        return qs.filter(event=event) if event else qs


@python_2_unicode_compatible
class Occurrence(models.Model):
    """
    Represents the start end time for a specific occurrence of a master ``Event``
    object.
    """
    event = models.ForeignKey(
        Event,
        verbose_name=_('event'),
        editable=False,
        related_name="occurrences")
    schedule = models.ForeignKey(
        Schedule,
        verbose_name=_('schedule'),
        editable=False,
        related_name="occurrences")
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))

    objects = OccurrenceManager()

    class Meta:
        verbose_name = _('occurrence')
        verbose_name_plural = _('occurrences')
        ordering = ('start_time', 'end_time')

    def __str__(self):
        return u'{}: {}'.format(self.title, self.start_time.isoformat())

    @models.permalink
    def get_absolute_url(self):
        return ('eventcalendar-occurrence', [str(self.event.id), str(self.id)])

    def __lt__(self, other):
        return self.start_time < other.start_time

    @property
    def title(self):
        return self.event.title

    @property
    def event_type(self):
        return self.event.event_type
