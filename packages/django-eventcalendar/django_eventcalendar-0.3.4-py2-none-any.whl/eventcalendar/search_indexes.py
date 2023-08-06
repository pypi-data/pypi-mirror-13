from six import iteritems
from django.contrib.contenttypes.models import ContentType
from elasticsearch_dsl import (DocType, String, Date, Boolean, Double, GeoPoint,
                               Long, Nested, analyzer)

html_strip = analyzer('html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


class OccurrenceDoc(DocType):
    event_url = String()
    title = String()
    slug = String()
    description = String(
        analyzer=html_strip,
        fields={'raw': String(index='not_analyzed')}
    )
    category = String(multi=True)
    category_type = String(multi=True)
    location_name = String()
    parsable_address = Boolean()
    raw_location = String()
    street_address = String()
    city = String()
    state = String()
    zipcode = String()
    latlong = GeoPoint()
    neighborhood = String()
    min_age = Long()
    max_age = Long()
    more_info_url = String()
    more_info_phone = String()
    tickets_url = String()
    image = String()
    image_width = Long()
    image_height = Long()
    price_info = Nested(properties={'description': String(), 'price': Double()})
    origin = String()
    start_time = Date()
    end_time = Date()

    class Meta:
        index = 'eventcalendar'

    def add_price(self, description, price):
        self.comments.append(
            {'description': description, 'price': price})

    @classmethod
    def from_model(cls, model):
        doc = cls()
        doc.meta.id = doc.prepare_id(model)
        fields = cls._doc_type.mapping.properties.to_dict().values()[0]['properties']
        for k in iteritems(fields):
            func_name = "prepare_%s" % k[0]
            func = getattr(doc, func_name, None)
            attr = getattr(model, k[0], None)
            if func is not None:
                setattr(doc, k[0], func(model))
            elif attr is not None:
                setattr(doc, k[0], attr)
        return doc

    def prepare_id(self, obj):
        ctype = ContentType.objects.get_for_model(obj)
        pk = str(obj.pk)
        origin = obj.event.origin
        return ".".join([ctype.app_label, ctype.model, origin, pk])

    def prepare_event_url(self, obj):
        return obj.event.get_absolute_url()

    def prepare_title(self, obj):
        return obj.event.title

    def prepare_slug(self, obj):
        return obj.event.slug

    def prepare_description(self, obj):
        return obj.event.description

    def prepare_category(self, obj):
        return obj.event.category.name

    def prepare_category_type(self, obj):
        return obj.event.category.event_type

    def prepare_parsable_address(self, obj):
        return obj.event.parsable_address

    def prepare_location_name(self, obj):
        if obj.event.venue:
            return obj.event.venue.name
        else:
            return obj.event.location_name or ''

    def prepare_raw_location(self, obj):
        if obj.event.venue:
            return obj.event.venue.address
        else:
            return obj.event.raw_location or ''

    def prepare_street_address(self, obj):
        if obj.event.parsable_address:
            return obj.event.location_street
        else:
            return ''

    def prepare_city(self, obj):
        if obj.event.parsable_address:
            return obj.event.location_city
        else:
            return ''

    def prepare_state(self, obj):
        if obj.event.parsable_address:
            return obj.event.location_state
        else:
            return ''

    def prepare_zipcode(self, obj):
        if obj.event.parsable_address:
            return obj.event.location_zip
        else:
            return ''

    def prepare_latlong(self, obj):
        if obj.event.venue and obj.event.venue.latlong:
            pnt_lng, pnt_lat = obj.event.venue.latlong.get_coords()
            return "%s,%s" % (pnt_lat, pnt_lng)
        elif obj.event.latlong:
            pnt_lng, pnt_lat = obj.event.latlong.get_coords()
            return "%s,%s" % (pnt_lat, pnt_lng)

    def prepare_neighborhood(self, obj):
        if obj.event.venue and obj.event.venue.neighborhood:
            return obj.event.venue.neighborhood.name
        elif obj.event.neighborhood:
            return obj.event.neighborhood.name

    def prepare_min_age(self, obj):
        if obj.event.min_age:
            return obj.event.min_age
        else:
            return 0

    def prepare_max_age(self, obj):
        if obj.event.max_age:
            return obj.event.max_age
        else:
            return 100

    def prepare_more_info_url(self, obj):
        if obj.event.more_info_url:
            return obj.event.more_info_url
        else:
            return ''

    def prepare_more_info_phone(self, obj):
        if obj.event.more_info_phone:
            return obj.event.more_info_phone
        else:
            return ''

    def prepare_tickets_url(self, obj):
        if obj.event.tickets_url:
            return obj.event.tickets_url
        else:
            return ''

    def prepare_image(self, obj):
        if obj.event.image:
            return obj.event.image.url
        else:
            return ''

    def prepare_image_width(self, obj):
        if obj.event.image_width:
            return obj.event.image_width
        else:
            return None

    def prepare_image_height(self, obj):
        if obj.event.image_height:
            return obj.event.image_height
        else:
            return None

    def prepare_price_info(self, obj):
        out = []
        try:
            for key, val in obj.event.price_info:
                out.append({'description': key, 'price': val})
        except ValueError:
            pass
        return out

    def prepare_origin(self, obj):
        if obj.event.origin:
            return obj.event.origin
        else:
            return ''

    def prepare_start_time(self, obj):
        if obj.start_time:
            return obj.start_time
        else:
            return ''

    def prepare_end_time(self, obj):
        if obj.end_time:
            return obj.end_time
        else:
            return ''
