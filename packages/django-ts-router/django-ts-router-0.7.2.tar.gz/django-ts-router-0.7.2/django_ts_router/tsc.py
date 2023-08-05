# vim:fileencoding=utf-8
import logging
import subprocess
import tempfile
import os
import os.path

from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_TSC_PATHS = [
    '/usr/bin/tsc',
    '/usr/local/bin/tsc',
]


def run(ts_src, dest):
    tsc = _find_tsc_command_path()
    if not tsc:
        raise LookupError('tsc command cannot be found. Set tsc path to "TSC" option in TS_ROUTER setting.')

    _, filepath = tempfile.mkstemp(suffix='.ts')
    try:
        with open(filepath, 'w') as f:
            f.write(ts_src)
        subprocess.call([tsc, '--removeComments', '--out', dest, filepath])
    finally:
        os.remove(filepath)


def transpile(ts_src):
    """Transpiles the given TypeScript code to JavaScript code and returns it.

    :return: Transpiled JavaScript code
    :rtype: str
    """
    _, filepath = tempfile.mkstemp(suffix='.js')
    try:
        run(ts_src, filepath)
        with open(filepath, 'r') as f:
            return f.read()
    finally:
        os.remove(filepath)


def _find_tsc_command_path():
    tsc = settings.TS_ROUTER.get('TSC')
    if tsc:
        return tsc

    for path in DEFAULT_TSC_PATHS:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
