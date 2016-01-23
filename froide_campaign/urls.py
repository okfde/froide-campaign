from django.conf.urls import url

from .views import index, campaign_page

urlpatterns = [
    url(r'^$', index, name='campaign-index'),
    url(r'^(?P<campaign_slug>[-\w]+)/$', campaign_page, name='campaign-page'),
]
