from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    # url(
    #     r'^$',
    #     views.OccurrenceList.as_view(),
    #     name='eventcalendar-index'
    # ),
    url(
        r'^$',
        views.OccurrenceSearchView.as_view(),
        name='eventcalendar-index'
    ),
    url(
        r'^parse/$',
        views.parsable,
        name='eventcalendar-parsable',
    ),
    url(
        r'^venues/$',
        views.VenueList.as_view(),
        name='eventcalendar-venue-list'
    ),
    url(
        r'^event/add/$',
        views.EventCreate.as_view(),
        name='eventcalendar-add-event'
    ),
    url(
        r'^event/(?P<slug>[-\w]+)/$',
        views.EventView.as_view(),
        name='eventcalendar-event'
    ),
    url(
        r'^event/(?P<slug>[-\w]+)/edit/$',
        views.EventUpdate.as_view(),
        name='eventcalendar-edit-event'
    ),
    url(
        r'^event/(?P<slug>[-\w]+)/delete/$',
        views.EventDelete.as_view(),
        name='eventcalendar-delete-event'
    ),
    url(
        r'^(?P<slug>[\w-]+)/$',
        views.EventCategoryDetail.as_view(),
        name='eventcalendar-category'
    ),
    # url(
    #     r'^(?P<slug>[-\w]+)/(\d+)/$',
    #     views.occurrence_view,
    #     name='eventcalendar-occurrence'
    # ),
)
