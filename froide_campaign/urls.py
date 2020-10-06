from django.conf.urls import url

from froide.helper import api_router

from .views import (
    index, campaign_page,
    CampaignPageListView, CampaignPageEditView, AssignCampaignPageTeamView,
    CampaignPageEmbedView, CampaignPageUpdateEmbedView,
    redirect_to_make_request, CampaignStatistics
)
from .api_views import InformationObjectViewSet

urlpatterns = [
    url(r'^$', index, name='campaign-index'),
    url(r'^list/$', CampaignPageListView.as_view(), name='campaign-list'),
    url(r'^request/(?P<campaign_id>\d+)/(?P<ident>[-\w\d]+)/$',
        redirect_to_make_request, name='campaign-redirect_to_make_request'),
    url(r'^(?P<slug>[-\w]+)/$', campaign_page, name='campaign-page'),
    url(r'^(?P<slug>[-\w]+)/edit/$', CampaignPageEditView.as_view(),
        name='campaign-edit'),
    url(r'^(?P<slug>[-\w]+)/set-team/$', AssignCampaignPageTeamView.as_view(),
        name='campaign-set_team'),
    url(r'^(?P<slug>[-\w]+)/embed/$', CampaignPageEmbedView.as_view(),
        name='campaign-embed'),
    url(r'^(?P<slug>[-\w]+)/update-embed/$',
        CampaignPageUpdateEmbedView.as_view(),
        name='campaign-updated_embed'),
    url(r'^(?P<slug>[-\w]+)/_stats/$',
        CampaignStatistics.as_view(),
        name='campaign-statisitcs')
]


api_router.register(
    r'campaigninformationobject',
    InformationObjectViewSet,
    basename='campaigninformationobject'
)
