from django.urls import path

from froide.helper import api_router

from .views import (
    index, campaign_page,
    CampaignPageListView, CampaignPageEditView, AssignCampaignPageTeamView,
    CampaignPageEmbedView, CampaignPageUpdateEmbedView,
    redirect_to_make_request, CampaignStatistics
)
from .api_views import InformationObjectViewSet

urlpatterns = [
    path('', index, name='campaign-index'),
    path('list/', CampaignPageListView.as_view(), name='campaign-list'),
    path('request/<int:campaign_id>/<slug:ident>/',
         redirect_to_make_request, name='campaign-redirect_to_make_request'),
    path('<slug:slug>/', campaign_page, name='campaign-page'),
    path('<slug:slug>/edit/', CampaignPageEditView.as_view(),
         name='campaign-edit'),
    path('<slug:slug>/set-team/', AssignCampaignPageTeamView.as_view(),
         name='campaign-set_team'),
    path('<slug:slug>/embed/', CampaignPageEmbedView.as_view(),
         name='campaign-embed'),
    path('<slug:slug>/update-embed/',
         CampaignPageUpdateEmbedView.as_view(),
         name='campaign-updated_embed'),
    path('<slug:slug>/_stats/',
         CampaignStatistics.as_view(),
         name='campaign-statisitcs')
]


api_router.register(
    r'campaigninformationobject',
    InformationObjectViewSet,
    basename='campaigninformationobject'
)
