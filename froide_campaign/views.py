from django.shortcuts import render, get_object_or_404, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext_lazy as _
from django.http import QueryDict
from django.db.models import Q
from django import forms

import django_filters

from froide.helper.cache import cache_anonymous_page

from .models import CampaignPage, InformationObject


@cache_anonymous_page(15 * 60)
def index(request):
    return render(request, 'froide_campaign/index.html', {
        'campaigns': CampaignPage.objects.filter(public=True),
    })


def filter_status(qs, status):
    if status:
        if status == '0':
            qs = qs.filter(foirequest__isnull=True)
        elif status == '1':
            qs = qs.filter(foirequest__isnull=False).exclude(
                           foirequest__status='resolved')
        elif status == '2':
            qs = qs.filter(foirequest__isnull=False,
                           foirequest__status='resolved')
    return qs


class InformationObjectFilterSet(django_filters.FilterSet):
    STATUS_CHOICES = (
        ('', _('All')),
        (0, _('No request yet')),
        (1, _('Pending request')),
        (2, _('Resolved request')),
    )
    q = django_filters.MethodFilter(action='filter_query')
    page = django_filters.NumberFilter(action=lambda x, y: x,
                                       widget=forms.HiddenInput)

    status = django_filters.ChoiceFilter(
            choices=STATUS_CHOICES,
            action=filter_status,
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
        self.base_filters['campaign'] = django_filters.ModelChoiceFilter(queryset=self.campaigns,
        widget=django_filters.widgets.LinkWidget, method='filter_campaign')
        super(InformationObjectFilterSet, self).__init__(*args, **kwargs)

    def filter_campaign(self, queryset, name, value):
        return queryset.filter(campaign=value)

    def filter_query(self, queryset, value):
        return queryset.filter(Q(title__icontains=value) |
                               Q(ident__icontains=value))


@cache_anonymous_page(15 * 60)
def campaign_page(request, slug):
    campaign_page = get_object_or_404(CampaignPage, slug=slug)
    if not campaign_page.public and not request.user.is_staff:
        raise Http404

    campaigns = campaign_page.campaigns.all()
    qs = InformationObject.objects.filter(campaign__in=campaigns)

    total_count = qs.count()
    pending_count = qs.filter(foirequest__isnull=False).count()
    done_count = qs.filter(foirequest__status='resolved').count()
    pending_count -= done_count

    qs = qs.select_related('campaign')

    filtered = InformationObjectFilterSet(request.GET, queryset=qs, campaigns=campaigns)

    if request.GET.get('random'):
        filtered = qs.filter(foirequest__isnull=True).order_by('?')

    page = request.GET.get('page')
    paginator = Paginator(filtered, 100)
    try:
        iobjs = paginator.page(page)
    except PageNotAnInteger:
        iobjs = paginator.page(1)
    except EmptyPage:
        iobjs = paginator.page(paginator.num_pages)

    no_page_query = QueryDict(request.GET.urlencode().encode('utf-8'),
                              mutable=True)
    no_page_query.pop('page', None)

    return render(request, 'froide_campaign/campaign.html', {
        'campaign_page': campaign_page,
        'object_list': iobjs,
        'filtered': filtered,
        'getvars': '&' + no_page_query.urlencode(),  # pagination
        'total_count': total_count,
        'done_count': done_count,
        'pending_count': pending_count,
        'getvars_complete': request.GET.urlencode(),
        'progress_pending': 0 if total_count == 0 else str(
                round(pending_count / float(total_count) * 100, 1)),
        'progress_done': 0 if total_count == 0 else str(
                round(done_count / float(total_count) * 100, 1)),
    })
