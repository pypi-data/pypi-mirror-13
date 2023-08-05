# vim:fileencoding=utf-8
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class DjangoTSRouterConfig(AppConfig):
    name = 'django_ts_router'
