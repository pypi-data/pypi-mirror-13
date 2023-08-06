from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = "Load geodata for neighborhoods."

    def handle_noargs(self, **options):
        from eventcalendar import load_geodata
        from django.core import management
        from eventcalendar.models import Venue
        load_geodata.run(options['verbosity'])
        management.call_command('loaddata', 'eventtypes', verbosity=0, interactive=False)
        management.call_command('loaddata', 'venuetypes', verbosity=0, interactive=False)
        management.call_command('loaddata', 'venues', verbosity=0, interactive=False)
        for v in Venue.objects.all():
            v.save()  # This will set the neighborhood
