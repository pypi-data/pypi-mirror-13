'''
Common features and functions
'''
from django.utils import six
import calendar
from datetime import datetime, date, timedelta
import itertools

from django.utils.safestring import mark_safe
from django.core.paginator import Paginator, Page
import usaddress


def geocode(address):
    """
    Attempt to geocode an address

    Returns either a Point or None
    """
    from geopy.geocoders import Nominatim
    from geopy.exc import GeopyError
    from django.contrib.gis.geos import Point

    geolocator = Nominatim(country_bias="us")
    try:
        l = geolocator.geocode(address)
        return Point(l.longitude, l.latitude)
    except (GeopyError, AttributeError):
        return None


def reverse_geocode(longitude, latitude):
    """
    Attempt to reverse geocode an address

    Returns either a place or None
    """
    from geopy.geocoders import Nominatim
    from geopy.exc import GeopyError
    from django.contrib.gis.geos import Point

    geolocator = Nominatim()
    try:
        return geolocator.reverse(Point(longitude, latitude))
    except (GeopyError, AttributeError):
        return None


def parse_address(address_string):
    try:
        tagged_address, address_type = usaddress.tag(address_string)
        name = []
        street = []
        street_2 = []
        city = ''
        state = ''
        zipcode = ''
        for partname, addr_part in tagged_address.items():
            if partname == 'PlaceName':
                city = addr_part
            elif partname == 'StateName':
                state = addr_part
            elif partname == 'ZipCode':
                zipcode = addr_part
            elif partname in ('Recipient', 'BuildingName', 'LandmarkName'):
                name.append(addr_part)
            elif 'Occupancy' in partname:
                street_2.append(addr_part)
            else:
                street.append(addr_part)
        street = " ".join(street)
        street_2 = " ".join(street_2)
        name = " ".join(name)
        return {
            'name': name,
            'street': street,
            'street_2': street_2,
            'city': city,
            'state': state,
            'zipcode': zipcode
        }, address_type
    except usaddress.RepeatedLabelError:
        return address_string, 'BadAddress'


def geocodable(address_string):
    """
    Can we possibly geocode this address?
    """
    try:
        address_string = address_string.strip()
        if not address_string:
            return False
    except ValueError:
        return False
    parsed_address, address_type = parse_address(address_string)
    return (address_type not in ('PO Box', 'Ambiguous', 'Bad Address'))


def html_mark_safe(func):
    '''
    Decorator for functions return strings that should be treated as template
    safe.

    '''
    def decorator(*args, **kws):
        return mark_safe(func(*args, **kws))
    return decorator


def time_delta_total_seconds(time_delta):
    '''
    Calculate the total number of seconds represented by a
    ``datetime.timedelta`` object

    '''
    return time_delta.days * 3600 + time_delta.seconds


def month_boundaries(dt=None):
    '''
    Return a 2-tuple containing the datetime instances for the first and last
    dates of the current month or using ``dt`` as a reference.

    '''
    dt = dt or date.today()
    wkday, ndays = calendar.monthrange(dt.year, dt.month)
    start = datetime(dt.year, dt.month, 1)
    return (start, start + timedelta(ndays - 1))


def default_css_class_cycler():
    return itertools.cycle(('evt-even', 'evt-odd'))


def generate_url(url, action_string):
    import os
    from hashlib import sha1
    from django.conf import settings
    transmogrify_key = getattr(settings, 'TRANSMOGRIFY_SECRET_KEY', settings.SECRET_KEY)
    security_hash = sha1(action_string + transmogrify_key).hexdigest()
    base_url, ext = os.path.splitext(url)

    return "%s%s%s?%s" % (base_url, action_string, ext, security_hash)


def fill_box(orig_dims, dest_dims):
    """
    orig_dims = (w, h)
    dest_dims = (w, h)
    crop = optional (l, t, r, b) - Use this crop to determine scale, what to crop.
    origin  = optional ('tl', 't', 'tr', 'l', 'c', 'r', 'bl', 'b', 'br')

    Returns the (l, t, r, b) crop to fill the dest_dims
    """
    # raise ValueError("'origin' parameter must be one of %s." % ", ".join((TOP, LEFT, CENTER, RIGHT, BOTTOM)))
    orig_width, orig_height = orig_dims
    dest_width, dest_height = dest_dims

    # Scale dest size to original size to find the crop (transmogrify will scale it back down)
    width_ratio = float(orig_width) / dest_width
    height_ratio = float(orig_height) / dest_height
    ratio = max(width_ratio, height_ratio)
    new_dest_width = int(dest_width * ratio)
    new_dest_height = int(dest_height * ratio)
    if new_dest_width > orig_width or new_dest_height > orig_height:
        ratio = min(width_ratio, height_ratio)
        new_dest_width = int(dest_width * ratio)
        new_dest_height = int(dest_height * ratio)

    xdiff = abs(orig_width - new_dest_width)
    ydiff = abs(orig_height - new_dest_height)
    if ydiff:
        # "Pad height"
        padding1 = ydiff / 2
        return (0, padding1, new_dest_width, padding1 + new_dest_height)
    else:
        # "Pad width"
        padding1 = xdiff / 2
        return (padding1, 0, padding1 + new_dest_width, new_dest_height)


def fit_to_box(orig_dims, dest_width=20000, dest_height=20000):
    """
    Given a width, height or both, it will return the width and height to
    fit in the given area.
    """
    im_width, im_height = orig_dims

    if dest_width == 20000 and dest_height == 20000:
        return im_width, im_height
    elif dest_width is None:
        dest_width = 20000
    elif dest_height is None:
        dest_height = 20000

    if dest_width < dest_height:
        scale = float(dest_width) / float(im_width)
        dest_height = int(round(scale * im_height))
    else:
        scale = float(dest_height) / float(im_height)
        dest_width = int(round(scale * im_width))

    return dest_width, dest_height


class ElasticSearchPaginator(Paginator):
    def _get_count(self):
        """
        Returns the total number of objects, across all pages.
        """
        if self._count is None:
            if not hasattr(self.object_list, 'hits'):
                self.object_list.execute()

            try:
                self._count = self.object_list.hits
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)
        return self._count

    def _get_page(self, *args, **kwargs):
        """
        Returns an instance of a single page.

        This hook can be used by subclasses to use an alternative to the
        standard :cls:`Page` object.
        """
        return ElasticSearchPage(*args, **kwargs)


class ElasticSearchPage(Page):
    def __len__(self):
        if hasattr(self.object_list, 'execute'):
            self.object_list = self.object_list.execute()
        return len(self.object_list)

    def __getitem__(self, index):
        if not isinstance(index, (slice,) + six.integer_types):
            raise TypeError
        # The object_list is converted to a list so that if it was a QuerySet
        # it won't be a database hit per __getitem__.
        if hasattr(self.object_list, 'execute'):
            self.object_list = self.object_list.execute()
        return self.object_list[index]
