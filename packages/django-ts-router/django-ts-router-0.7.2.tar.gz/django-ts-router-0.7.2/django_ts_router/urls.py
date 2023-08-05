# vim:fileencoding=utf-8
from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    url(r'^router.js$', cache_page(300)(views.RouterJSView.as_view()), name='django_ts_router_js'),
]
