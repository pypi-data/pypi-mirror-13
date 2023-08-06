from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = "Load geodata for neighborhoods."

    def handle_noargs(self, **options):
        import datetime
        from eventcalendar.search_indexes import OccurrenceDoc
        from eventcalendar.models import Occurrence
        from haystack import connections as haystack_connections
        from elasticsearch_dsl.connections import connections
        from elasticsearch_dsl.exceptions import IllegalOperation

        backend = haystack_connections['eventcalendar'].get_backend()
        connections.add_connection('default', backend.conn)
        try:
            OccurrenceDoc.init()  # This is to make sure the index exists
        except IllegalOperation:
            pass

        occurrences = Occurrence.objects.filter(start_time__gte=datetime.datetime.now())

        for o in occurrences:
            doc = OccurrenceDoc.from_model(o)
            doc.save()
