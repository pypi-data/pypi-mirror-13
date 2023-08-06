from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.utils.timezone import now
from django.views.generic.edit import DeleteView  # , CreateView, UpdateView
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormMixin
from django.views.decorators.csrf import ensure_csrf_cookie

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet

from .models import Event, EventCategory, Occurrence, Schedule, Venue
from .forms import EventForm, ScheduleForm, ScheduleFormHelper, OccurrenceSearchForm
from .utils import ElasticSearchPaginator


def parsable(request):
    """
    Given a string, attempt to address parse it. Return a boolean for success.
    """
    from .utils import parse_address
    geocodable = False
    address = request.get('address', '')
    if address:
        parsed_address, address_type = parse_address(address)
        geocodable = (address_type not in ('PO Box', 'Ambiguous', 'Bad Address'))
    return JsonResponse({'success': geocodable})


@ensure_csrf_cookie
def reverse_geolocate(request):
    """
    return a location when given a lat and long
    """
    if request.method == 'post':
        return


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class ScheduleInline(InlineFormSet):
    model = Schedule
    extra = 1
    form_class = ScheduleForm


class EventCategoryDetail(DetailView):
    model = EventCategory


class OccurrenceList(ListView):
    model = Occurrence

    def get_queryset(self):
        return self.model.objects.filter(end_time__gt=now())


class EventView(DetailView):
    model = Event


class EventCreate(LoginRequiredMixin, CreateWithInlinesView):
    model = Event
    form_class = EventForm
    inlines = [ScheduleInline]

    def get_context_data(self, *args, **kwargs):
        ctxt = super(EventCreate, self).get_context_data(*args, **kwargs)
        ctxt.update({'schedule_helper': ScheduleFormHelper()})
        return ctxt

    def forms_valid(self, form, inlines):
        form.instance.submitter = self.request.user
        self.object = form.save()
        for formset in inlines:
            formset.save()
        return HttpResponseRedirect(self.get_success_url())


class EventUpdate(LoginRequiredMixin, UpdateWithInlinesView):
    model = Event
    form_class = EventForm
    inlines = [ScheduleInline]

    def get_template_names(self):
        if not getattr(self, 'user_can_edit', False):
            return ['eventcalendar/bad_user.html']
        return super(EventUpdate, self).get_template_names()

    def get_context_data(self, *args, **kwargs):
        ctxt = super(EventUpdate, self).get_context_data(*args, **kwargs)
        ctxt.update({'schedule_helper': ScheduleFormHelper()})
        return ctxt

    def post(self, request, *args, **kwargs):
        if request.user.is_staff or request.user == self.object.user:
            self.user_can_edit = True
        else:
            self.user_can_edit = False
        return super(EventUpdate, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # self.object = self.get_object()
        if request.user.is_staff or request.user == self.object.user:
            self.user_can_edit = True
        else:
            self.user_can_edit = False
        # context = self.get_context_data(object=self.object)
        # return self.render_to_response(context)
        return super(EventUpdate, self).get(request, *args, **kwargs)


class EventDelete(LoginRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('eventcalendar-index')


class VenueList(ListView):
    model = Venue

    def get_queryset(self):
        qset = super(VenueList, self).get_queryset()
        if 'search' in self.request.GET:
            return qset.filter(name__istartswith=self.request.GET.get('search', ''))
        return qset

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        return context

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        object_list = self.get_data(context)['object_list']
        return JsonResponse(
            list(object_list.values('name', 'address', 'id')),
            safe=False,
            **response_kwargs
        )

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class OccurrenceSearchView(FormMixin, ListView):
    template_name = 'eventcalendar/occurrence_search_list.html'
    facet_fields = ['category', 'neighborhood']
    form_class = OccurrenceSearchForm
    load_all = False
    paginate_by = 20
    paginator_class = ElasticSearchPaginator

    def get(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())

        if form.is_valid():
            self.object_list = form.search()

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(OccurrenceSearchView, self).get_form_kwargs()

        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
                'files': self.request.FILES,
            })
        return kwargs

    def form_invalid(self, form):
        self.queryset = form.no_query_found()
        context = self.get_context_data(**{
            self.form_name: form,
            'object_list': self.queryset
        })
        return self.render_to_response(context)

    # def get_context_data(self, **kwargs):
    #     context = super(OccurrenceSearchView, self).get_context_data(**kwargs)
    #     return context

    def get_queryset(self):
        return self.object_list

    def get_data(self, context):
        from django.template.loader import render_to_string
        template_name = '_widgets/_occurrence_tile_by_date.html'
        rendered = render_to_string(template_name, context)
        return {'html': rendered}

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def render_to_response(self, context, **response_kwargs):
        len(context['page_obj'])  # This forces the execution of the query. Sometimes it doesn't happen otherwise
        if self.request.is_ajax():
            return self.render_to_json_response(context, **response_kwargs)
        return super(OccurrenceSearchView, self).render_to_response(context, **response_kwargs)
