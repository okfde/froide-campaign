from django.urls import path
from froide.api import api_router

from .api_views import InformationObjectViewSet
from .views import (
    AssignCampaignPageTeamView,
    CampaignPageEditView,
    CampaignPageEmbedView,
    CampaignPageListView,
    CampaignPageUpdateEmbedView,
    CampaignStatistics,
    add_campaign_report,
    campaign_page,
    index,
    redirect_to_make_request,
)

urlpatterns = [
    path("", index, name="campaign-index"),
    path("list/", CampaignPageListView.as_view(), name="campaign-list"),
    path(
        "request/<int:campaign_id>/<slug:ident>/",
        redirect_to_make_request,
        name="campaign-redirect_to_make_request",
    ),
    path("<slug:slug>/", campaign_page, name="campaign-page"),
    path("<slug:slug>/edit/", CampaignPageEditView.as_view(), name="campaign-edit"),
    path(
        "<slug:slug>/set-team/",
        AssignCampaignPageTeamView.as_view(),
        name="campaign-set_team",
    ),
    path("<slug:slug>/embed/", CampaignPageEmbedView.as_view(), name="campaign-embed"),
    path(
        "<slug:slug>/update-embed/",
        CampaignPageUpdateEmbedView.as_view(),
        name="campaign-updated_embed",
    ),
    path(
        "<slug:slug>/_stats/", CampaignStatistics.as_view(), name="campaign-statisitcs"
    ),
    path(
        "report/<int:questionaire_id>/<int:iobj_id>/<int:foirequest_id>/",
        add_campaign_report,
        name="campaign-add_campaign_report",
    ),
]


api_router.register(
    r"campaigninformationobject",
    InformationObjectViewSet,
    basename="campaigninformationobject",
)
