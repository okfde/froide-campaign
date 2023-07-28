from django import forms
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, F
from django.http import QueryDict
from django.shortcuts import Http404, get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import DetailView, ListView

import django_filters
from parler.views import TranslatableSlugMixin

from froide.campaign.models import Campaign as FroideCampaign
from froide.foirequest.auth import can_write_foirequest
from froide.foirequest.models.request import FoiRequest
from froide.helper.auth import (
    can_access_object,
    can_manage_object,
    can_read_object,
    get_read_queryset,
)
from froide.helper.cache import cache_anonymous_page
from froide.helper.utils import render_403
from froide.team.forms import AssignTeamForm
from froide.team.views import AssignTeamView

from .forms import QuestionaireForm
from .models import Campaign, CampaignPage, InformationObject, Questionaire
from .utils import make_embed


@cache_anonymous_page(15 * 60)
def index(request):
    return render(
        request,
        "froide_campaign/index.html",
        {
            "campaign_pages": CampaignPage.objects.filter(public=True),
        },
    )


def filter_status(qs, name, status):
    if status:
        if status == "0":
            qs = qs.filter(foirequest__isnull=True, resolved=False)
        elif status == "1":
            qs = qs.filter(foirequest__isnull=False, resolved=False).exclude(
                foirequest__status="resolved"
            )
        elif status == "2":
            qs = qs.filter(
                foirequest__isnull=False, resolved=False, foirequest__status="resolved"
            )
        elif status == "3":
            qs = qs.filter(resolved=True)
    return qs


class InformationObjectFilterSet(django_filters.FilterSet):
    STATUS_CHOICES = (
        (0, _("No request yet")),
        (1, _("Pending request")),
        (2, _("Resolved request")),
        (3, _("Information already public")),
    )
    q = django_filters.CharFilter(method="filter_query")
    page = django_filters.NumberFilter(
        method=lambda x, y, z: x, widget=forms.HiddenInput
    )

    status = django_filters.ChoiceFilter(
        choices=STATUS_CHOICES,
        method=filter_status,
        widget=django_filters.widgets.LinkWidget,
    )

    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ("-ordering", "ordering"),
            ("first_name", "first_name"),
            ("last_name", "last_name"),
        ),
    )

    class Meta:
        model = InformationObject
        fields = ["status", "page", "q", "campaign"]

    def __init__(self, *args, **kwargs):
        self.campaigns = kwargs.pop("campaigns")
        self.base_filters["campaign"] = django_filters.ModelChoiceFilter(
            queryset=self.campaigns,
            widget=django_filters.widgets.LinkWidget,
            method="filter_campaign",
        )
        super(InformationObjectFilterSet, self).__init__(*args, **kwargs)

    def filter_campaign(self, queryset, name, value):
        return queryset.filter(campaign=value)

    def filter_query(self, queryset, name, value):
        return InformationObject.objects.search(queryset, value)


def get_campaign_stats(campaign):
    campaigns = campaign.campaigns.all()
    qs = InformationObject.objects.filter(campaign__in=campaigns)
    qs = qs.select_related("foirequest")
    return get_information_object_stats(qs)


def get_information_object_stats(qs):
    total_count = qs.count()
    resolved_count = qs.filter(resolved=True).count()
    pending_count = qs.filter(foirequest__isnull=False).count()
    done_count = qs.filter(foirequest__status="resolved").count()

    pending_count -= done_count
    done_count += resolved_count
    return {
        "pending_count": pending_count,
        "total_count": total_count,
        "resolved_count": resolved_count,
        "done_count": done_count,
        "progress_pending": 0
        if total_count == 0
        else str(round(pending_count / float(total_count) * 100, 1)),
        "progress_done": 0
        if total_count == 0
        else str(round(done_count / float(total_count) * 100, 1)),
    }


@cache_anonymous_page(15 * 60)
def campaign_page(request, slug):
    campaign_page = get_object_or_404(CampaignPage, slug=slug)

    if not can_read_object(campaign_page, request):
        raise Http404

    campaigns = campaign_page.campaigns.all()
    qs = InformationObject.objects.filter(campaign__in=campaigns)
    qs = qs.select_related("foirequest")
    stats = get_information_object_stats(qs)
    qs = qs.select_related("campaign", "publicbody")

    cleaned_query = QueryDict(request.GET.urlencode().encode("utf-8"), mutable=True)
    random_qs = cleaned_query.pop("random", None)

    filterset = InformationObjectFilterSet(
        cleaned_query, queryset=qs, campaigns=campaigns
    )

    if random_qs:
        qs = qs.filter(foirequest__isnull=True).order_by("?")
    else:
        qs = filterset.qs

    page = request.GET.get("page")
    paginator = Paginator(qs, 100)
    try:
        iobjs = paginator.page(page)
    except PageNotAnInteger:
        iobjs = paginator.page(1)
    except EmptyPage:
        iobjs = paginator.page(paginator.num_pages)

    getvars_complete = cleaned_query.urlencode()

    cleaned_query.pop("page", None)
    getvars = cleaned_query.urlencode()

    context = {
        "campaign_page": campaign_page,
        "object_list": iobjs,
        "filtered": filterset,
        "getvars": "&" + getvars,  # pagination
        "getvars_complete": getvars_complete,
    }
    context.update(stats)

    return render(request, "froide_campaign/campaign.html", context)


def redirect_to_make_request(request, campaign_id, ident):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    provider = campaign.get_provider()
    obj = provider.get_by_ident(ident)
    url = provider.get_request_url(obj)
    return redirect(url)


class AuthRequiredMixin(object):
    AUTH_VERB = "write"

    def get_object(self, queryset=None):
        obj = super(AuthRequiredMixin, self).get_object(queryset=queryset)
        if not can_access_object(self.AUTH_VERB, obj, self.request):
            raise Http404
        return obj


class ReadAuthRequiredMixin(AuthRequiredMixin):
    AUTH_VERB = "read"


class CampaignPageListView(AuthRequiredMixin, ListView):
    model = CampaignPage
    template_name = "froide_campaign/list_campaign_page.html"

    def get_queryset(self):
        qs = super(CampaignPageListView, self).get_queryset()
        return get_read_queryset(qs, self.request, has_team=True)


class CampaignPageEditView(AuthRequiredMixin, DetailView):
    model = CampaignPage
    template_name = "froide_campaign/edit_campaign_page.html"

    def get_context_data(self, **kwargs):
        context = super(CampaignPageEditView, self).get_context_data(**kwargs)
        if can_manage_object(self.object, self.request):
            context["team_form"] = AssignTeamForm(
                instance=self.object, user=self.request.user
            )
        return context


class AssignCampaignPageTeamView(AssignTeamView):
    model = CampaignPage
    template_name = "froide_campaign/edit_campaign_page.html"

    def get_success_url(self):
        return reverse("campaign-edit", kwargs={"slug": self.object.slug})


@method_decorator(xframe_options_exempt, name="dispatch")
class CampaignPageEmbedView(ReadAuthRequiredMixin, DetailView):
    model = CampaignPage
    template_name = "froide_campaign/embed.html"

    def get_context_data(self, **kwargs):
        context = super(CampaignPageEmbedView, self).get_context_data(**kwargs)
        stats = get_campaign_stats(self.object)
        context.update(stats)
        return context


class CampaignPageUpdateEmbedView(AuthRequiredMixin, DetailView):
    model = CampaignPage
    template_name = "froide_campaign/edit_campaign_page.html"

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        return redirect(reverse("campaign-edit", kwargs={"slug": obj.slug}))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        stats = get_campaign_stats(self.object)
        context = {
            "object": self.object,
        }
        context.update(stats)
        make_embed(self.object.embed, CampaignPageEmbedView.template_name, context)
        self.object.save()
        return self.get(request)


class CampaignStatistics(TranslatableSlugMixin, DetailView):
    model = Campaign
    template_name = "froide_campaign/campaign_statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        context["stats"] = self.get_stats()
        return context

    def get_base_stats(self):
        base_stats = dict(
            request_count=Count("*"), user_count=Count("user_id", distinct=True)
        )
        return base_stats

    def agg_requests(self, qs):
        return qs.annotate(**self.get_base_stats()).order_by("-request_count")

    def get_stats(self):
        campaign = self.object

        froide_cat = FroideCampaign.objects.get(ident=campaign.slug)
        foirequest_total = FoiRequest.published.all()
        all_requests = foirequest_total.filter(campaign=froide_cat)
        aggregated = all_requests.aggregate(**self.get_base_stats())

        foirequest_success = FoiRequest.published.successful()
        success = foirequest_success.filter(campaign=froide_cat)

        by_jurisdiction = self.agg_requests(
            all_requests.annotate(
                population=F("public_body__jurisdiction__region__population")
            ).values("public_body__jurisdiction__name", "population"),
        )
        return {
            "all_requests": all_requests.count(),
            "successfull_requests": success.count(),
            "all_users": aggregated.get("user_count"),
            "by_jurisdiction": by_jurisdiction,
        }


def add_campaign_report(request, questionaire_id, iobj_id, foirequest_id):
    if not request.user.is_authenticated:
        return render_403(request)
    questionaire = get_object_or_404(Questionaire, id=questionaire_id)
    iobj = get_object_or_404(
        InformationObject, id=iobj_id, campaign=questionaire.campaign
    )
    foirequest = get_object_or_404(iobj.foirequests.all(), id=foirequest_id)
    if not can_write_foirequest(foirequest, request):
        return render_403(request)

    if request.method == "POST":
        form = QuestionaireForm(data=request.POST, questionaire=questionaire)
        if form.is_valid():
            form.save(request.user, iobj, foirequest)
            messages.add_message(
                request, messages.SUCCESS, _("Thank you, your answers were saved!")
            )

            return redirect(foirequest)
        messages.add_message(
            request, messages.ERROR, _("Please fix the errors in the form!")
        )
    else:
        form = QuestionaireForm(questionaire=questionaire)

    return render(
        request,
        "froide_campaign/questionaire.html",
        {"questionaire": questionaire, "form": form},
    )
