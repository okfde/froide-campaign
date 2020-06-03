from django.views.generic import DetailView, ListView
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, Http404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.http import QueryDict
from django import forms

import django_filters

from froide.team.forms import AssignTeamForm
from froide.team.views import AssignTeamView

from froide.helper.cache import cache_anonymous_page
from froide.helper.auth import (can_read_object, can_manage_object,
                                can_access_object, get_read_queryset)

from .models import CampaignPage, InformationObject
from .utils import make_embed


@cache_anonymous_page(15 * 60)
def index(request):
    return render(request, 'froide_campaign/index.html', {
        'campaign_pages': CampaignPage.objects.filter(public=True),
    })


def filter_status(qs, name, status):
    if status:
        if status == '0':
            qs = qs.filter(foirequest__isnull=True, resolved=False)
        elif status == '1':
            qs = qs.filter(foirequest__isnull=False, resolved=False).exclude(
                           foirequest__status='resolved')
        elif status == '2':
            qs = qs.filter(foirequest__isnull=False, resolved=False,
                           foirequest__status='resolved')
        elif status == '3':
            qs = qs.filter(resolved=True)
    return qs


class InformationObjectFilterSet(django_filters.FilterSet):
    STATUS_CHOICES = (
        (0, _('No request yet')),
        (1, _('Pending request')),
        (2, _('Resolved request')),
        (3, _('Information already public')),
    )
    q = django_filters.CharFilter(method='filter_query')
    page = django_filters.NumberFilter(method=lambda x, y, z: x,
                                       widget=forms.HiddenInput)

    status = django_filters.ChoiceFilter(
            choices=STATUS_CHOICES,
            method=filter_status,
            widget=django_filters.widgets.LinkWidget)

    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('-ordering', 'ordering'),
            ('first_name', 'first_name'),
            ('last_name', 'last_name'),
        ),
    )

    class Meta:
        model = InformationObject
        fields = ['status', 'page', 'q', 'campaign']

    def __init__(self, *args, **kwargs):
        self.campaigns = kwargs.pop('campaigns')
        self.base_filters['campaign'] = django_filters.ModelChoiceFilter(
            queryset=self.campaigns,
            widget=django_filters.widgets.LinkWidget, method='filter_campaign'
        )
        super(InformationObjectFilterSet, self).__init__(*args, **kwargs)

    def filter_campaign(self, queryset, name, value):
        return queryset.filter(campaign=value)

    def filter_query(self, queryset, name, value):
        return InformationObject.objects.search(queryset, value)


def get_campaign_stats(campaign):
    campaigns = campaign.campaigns.all()
    qs = InformationObject.objects.filter(campaign__in=campaigns)
    qs = qs.select_related('foirequest')
    return get_information_object_stats(qs)


def get_information_object_stats(qs):
    total_count = qs.count()
    resolved_count = qs.filter(resolved=True).count()
    pending_count = qs.filter(foirequest__isnull=False).count()
    done_count = qs.filter(foirequest__status='resolved').count()

    pending_count -= done_count
    done_count += resolved_count
    return {
        'pending_count': pending_count,
        'total_count': total_count,
        'resolved_count': resolved_count,
        'done_count': done_count,
        'progress_pending': 0 if total_count == 0 else str(
                round(pending_count / float(total_count) * 100, 1)),
        'progress_done': 0 if total_count == 0 else str(
                round(done_count / float(total_count) * 100, 1)),
    }


@cache_anonymous_page(15 * 60)
def campaign_page(request, slug):
    campaign_page = get_object_or_404(CampaignPage, slug=slug)

    if not can_read_object(campaign_page, request):
        raise Http404

    campaigns = campaign_page.campaigns.all()
    qs = InformationObject.objects.filter(campaign__in=campaigns)
    qs = qs.select_related('foirequest')
    stats = get_information_object_stats(qs)
    qs = qs.select_related('campaign', 'publicbody')

    cleaned_query = QueryDict(request.GET.urlencode().encode('utf-8'),
                              mutable=True)
    random_qs = cleaned_query.pop('random', None)

    filterset = InformationObjectFilterSet(
        cleaned_query, queryset=qs, campaigns=campaigns
    )

    if random_qs:
        qs = qs.filter(foirequest__isnull=True).order_by('?')
    else:
        qs = filterset.qs

    page = request.GET.get('page')
    paginator = Paginator(qs, 100)
    try:
        iobjs = paginator.page(page)
    except PageNotAnInteger:
        iobjs = paginator.page(1)
    except EmptyPage:
        iobjs = paginator.page(paginator.num_pages)

    getvars_complete = cleaned_query.urlencode()

    cleaned_query.pop('page', None)
    getvars = cleaned_query.urlencode()

    context = {
        'campaign_page': campaign_page,
        'object_list': iobjs,
        'filtered': filterset,
        'getvars': '&' + getvars,  # pagination
        'getvars_complete': getvars_complete,
    }
    context.update(stats)

    return render(request, 'froide_campaign/campaign.html', context)


class AuthRequiredMixin(object):
    AUTH_VERB = 'write'

    def get_object(self, queryset=None):
        obj = super(AuthRequiredMixin, self).get_object(queryset=queryset)
        if not can_access_object(self.AUTH_VERB, obj, self.request):
            raise Http404
        return obj


class ReadAuthRequiredMixin(AuthRequiredMixin):
    AUTH_VERB = 'read'


class CampaignPageListView(AuthRequiredMixin, ListView):
    model = CampaignPage
    template_name = 'froide_campaign/list_campaign_page.html'

    def get_queryset(self):
        qs = super(CampaignPageListView, self).get_queryset()
        return get_read_queryset(qs, self.request, has_team=True)


class CampaignPageEditView(AuthRequiredMixin, DetailView):
    model = CampaignPage
    template_name = 'froide_campaign/edit_campaign_page.html'

    def get_context_data(self, **kwargs):
        context = super(CampaignPageEditView, self).get_context_data(**kwargs)
        if can_manage_object(self.object, self.request):
            context['team_form'] = AssignTeamForm(
                instance=self.object,
                user=self.request.user
            )
        return context


class AssignCampaignPageTeamView(AssignTeamView):
    model = CampaignPage
    template_name = 'froide_campaign/edit_campaign_page.html'

    def get_success_url(self):
        return reverse('campaign-edit', kwargs={'slug': self.object.slug})


@method_decorator(xframe_options_exempt, name='dispatch')
class CampaignPageEmbedView(ReadAuthRequiredMixin, DetailView):
    model = CampaignPage
    template_name = 'froide_campaign/embed.html'

    def get_context_data(self, **kwargs):
        context = super(CampaignPageEmbedView, self).get_context_data(**kwargs)
        stats = get_campaign_stats(self.object)
        context.update(stats)
        return context


class CampaignPageUpdateEmbedView(AuthRequiredMixin, DetailView):
    model = CampaignPage
    template_name = 'froide_campaign/edit_campaign_page.html'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        return redirect(reverse('campaign-edit', kwargs={'slug': obj.slug}))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        stats = get_campaign_stats(self.object)
        context = {
            'object': self.object,
        }
        context.update(stats)
        make_embed(
            self.object.embed, CampaignPageEmbedView.template_name, context
        )
        self.object.save()
        return self.get(request)
