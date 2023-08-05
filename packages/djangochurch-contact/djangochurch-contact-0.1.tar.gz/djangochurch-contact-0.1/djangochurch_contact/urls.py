from blanc_basic_pages.views import lazy_page
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$',
        views.ContactFormView.as_view(),
        name='form'),
    url(r'^thanks/$',
        lazy_page,
        name='form-thanks'),
]
