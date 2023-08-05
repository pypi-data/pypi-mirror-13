# vim:fileencoding=utf-8
import logging

from django.http import HttpResponse
from django.views.generic import View

from . import tsc
from .route import Router

logger = logging.getLogger(__name__)


class RouterJSView(View):
    def get(self, *args, **kwargs):
        logger.debug("Generates router.js")
        ts_src = Router().export()
        js_src = tsc.transpile(ts_src)
        return HttpResponse(js_src, content_type='text/javascript')
