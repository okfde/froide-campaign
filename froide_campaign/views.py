from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from froide.helper.cache import cache_anonymous_page

from .models import Campaign, InformationObject


@cache_anonymous_page(15 * 60)
def index(request):
    return render(request, 'froide_campaign/index.html', {
        'campaigns': Campaign.objects.all(),
    })


@cache_anonymous_page(15 * 60)
def campaign_page(request, campaign_slug):
    campaign = get_object_or_404(Campaign, slug=campaign_slug)
    qs = InformationObject.objects.filter(campaign=campaign)

    query = request.GET.get('q')
    if query:
        qs = qs.filter(title__icontains=query)

    page = request.GET.get('page')
    paginator = Paginator(qs, 100)

    try:
        iobjs = paginator.page(page)
    except PageNotAnInteger:
        iobjs = paginator.page(1)
    except EmptyPage:
        iobjs = paginator.page(paginator.num_pages)

    return render(request, 'froide_campaign/campaign.html', {
        'campaign': campaign,
        'object_list': iobjs,
        'query': query
    })
