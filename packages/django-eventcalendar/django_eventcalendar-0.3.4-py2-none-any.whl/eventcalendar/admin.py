from django.contrib import admin
from .models import EventCategory, Event, Occurrence, Venue, Neighborhood, Schedule


class ScheduleInline(admin.TabularInline):
    model = Schedule
    fields = ('begins', 'duration', 'rrule_str')
    extra = 0


class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ('name', )


class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', )
    prepopulated_fields = {"slug": ("name",)}


class OccurrenceInline(admin.TabularInline):
    model = Occurrence
    extra = 1


def approve_events(modeladmin, request, queryset):
    """
    Mark events as approved
    """
    queryset.update(approved=True)
approve_events.short_description = "Mark selected events as approved"


class EventAdmin(admin.ModelAdmin):
    actions = (approve_events, )
    list_display = ('title', 'thumbnail', 'parsable_address', 'description', 'approved', )
    list_editable = ('approved', )
    list_display_links = ('title', 'thumbnail', )
    search_fields = ('title', 'description')
    inlines = [ScheduleInline, OccurrenceInline]
    raw_id_fields = ['venue', 'submitter', ]
    list_filter = ('approved', 'origin', 'category')

    def thumbnail(self, obj):
        if obj.image:
            return u'<img src="%s" width="120" height="80">' % obj.get_120x80_url()
        return u"No Image Available"
    thumbnail.allow_tags = True
    thumbnail.short_description = "Image"

    def parsable_address(self, obj):
        return obj.parsable_address
    parsable_address.boolean = True


class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'parsable_address', 'address')
    search_fields = ('name', 'address')
    prepopulated_fields = {"slug": ("name",)}

    def parsable_address(self, obj):
        return obj.parsable_address
    parsable_address.boolean = True

admin.site.register(Event, EventAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Neighborhood, NeighborhoodAdmin)
