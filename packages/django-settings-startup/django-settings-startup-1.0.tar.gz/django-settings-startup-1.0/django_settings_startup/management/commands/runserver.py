from django.conf import settings
from django.core.management.commands.runserver import Command as BaseCommand
from django.core.management.base import CommandError, handle_default_options
from optparse import make_option

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
    option_list = BaseCommand.option_list + (
        make_option(
            '--config', action='store_true', dest='use_config', default=False,
            help='Show your settings on output.'),
    )

    def inner_run(self, *args, **options):
        use_config = options.get('use_config')
        if use_config:
          print_settings()
        super(Command, self).inner_run(*args, **options)

