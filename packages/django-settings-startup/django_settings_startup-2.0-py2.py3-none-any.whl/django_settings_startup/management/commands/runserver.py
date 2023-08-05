from __future__ import print_function

from django.conf import settings
from django.core.management.commands.runserver import Command as BaseCommand

def print_settings():
    print("Settings django...")
    d = {}
    for attr in dir(settings):
            if not attr.startswith('__'):
                value = getattr(settings, attr)
                d[attr] = value
    keys = list(d.keys())
    keys.sort()
    for k in keys:
        print('%s = %r' % (k, d[k]))
    print("...OK\n")

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--config', action='store_true', dest='use_config', default=False,
            help='Show your settings on standard output.')
        super(Command, self).add_arguments(parser)

    def handle(self, *fixture_labels, **options):
        use_config = options.get('use_config')
        if use_config:
          print_settings()
        super(Command, self).handle(*fixture_labels, **options)

