# vim:fileencoding=utf-8
import logging

from django.core.management import BaseCommand

from django_ts_router import tsc
from django_ts_router.route import Router

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generates a TypeScript code for URL reverse function."

    def add_arguments(self, parser):
        parser.add_argument('--out',
                            action='store',
                            dest='out',
                            default=None,
                            help='Output a generated TypeScript code to the given file.')

        parser.add_argument('--module',
                            action='store',
                            dest='module',
                            default=None,
                            help='A module name to which the reverse() function belongs.')

        parser.add_argument('--javascript', '-j',
                            action='store_true',
                            dest='js',
                            default=False,
                            help='Generate a JavaScript code. "--out" option must be specified.')

    def handle(self, *args, **options):
        ts_src = Router().export(module=options['module'])

        if options['out']:
            if options['js']:
                tsc.run(ts_src, options['out'])
            else:
                with open(options['out'], 'w') as fp:
                    fp.write(ts_src)
        else:
            if options['js']:
                self.stdout.write(tsc.transpile(ts_src))
            else:
                self.stdout.write(ts_src)
