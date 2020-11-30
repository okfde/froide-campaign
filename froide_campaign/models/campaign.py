import functools
import json

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.gis.db import models as gis_models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template import Template, Context
from django.utils.http import urlquote
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.search import (SearchVectorField, SearchVector,
                                            SearchVectorExact, SearchQuery)

from froide.publicbody.models import PublicBody
from froide.foirequest.models import FoiRequest, FoiAttachment
from froide.team.models import Team
from froide.helper.csv_utils import export_csv

from froide_campaign.storage import OverwriteStorage


class SearchVectorStartsWith(SearchVectorExact):
    """This lookup scans for full text index entries that BEGIN with
    a given phrase, like:
    will get translated to
        ts_query('Foobar:* & Baz:* & Quux:*')
    """
    lookup_name = 'startswith'

    def process_rhs(self, qn, connection):
        if not hasattr(self.rhs, 'resolve_expression'):
            config = getattr(self.lhs, 'config', None)
            self.rhs = SearchQuery(self.rhs, config=config)
        rhs, rhs_params = super(SearchVectorExact, self).process_rhs(
            qn, connection
        )
        rhs = '(to_tsquery(%s::regconfig, %s))'
        parts = (s.replace("'", '') for s in rhs_params[1].split())
        rhs_params[1] = ' & '.join("'%s':*" % s for s in parts if s)
        return rhs, rhs_params

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s @@ %s' % (lhs, rhs), params


SearchVectorField.register_lookup(SearchVectorStartsWith)


def get_embed_path(instance, filename):
    return 'campaign/page/embed/{0}/index.html'.format(instance.slug)


class CampaignPage(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    description = models.TextField(blank=True)
    public = models.BooleanField(default=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("User")
    )
    team = models.ForeignKey(
        Team, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_("Team")
    )

    settings = JSONField(default=dict, blank=True)
    embed = models.FileField(
        blank=True, upload_to=get_embed_path,
        storage=OverwriteStorage()
    )

    campaigns = models.ManyToManyField('Campaign')

    class Meta:
        verbose_name = _('Campaign page')
        verbose_name_plural = _('Campaign pages')
        permissions = (
            ("can_use_campaigns", _("Can use campaigns")),
        )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('campaign-page', kwargs={'slug': self.slug})

    def get_absolute_domain_embed_url(self):
        return settings.SITE_URL + reverse('campaign-embed', kwargs={
            'slug': self.slug
        })

    def get_edit_iframe(self, url=None):
        if url is None:
            url = self.get_absolute_domain_embed_url()
        return format_html(
            '<iframe src="{}" class="froide-campaign" '
            'id="froide-campaign-{}" style="width:100%;border:0" '
            'frameborder="0"></iframe>',
            url,
            str(self.id)
        )

    def get_embed_iframe(self):
        if not self.embed:
            return ''
        url = self.embed.url
        if not url.startswith('http'):
            url = settings.SITE_URL + url
        return self.get_edit_iframe(url)

    @property
    def requires_foi(self):
        return all(c.requires_foi for c in self.campaigns.all())

    def is_public(self):
        # necessary for auth can_read_object
        return self.public


class CampaignManager(models.Manager):
    def get_public(self):
        return self.filter(public=True)


class Campaign(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    public = models.BooleanField(default=False)

    category = models.CharField(max_length=255, blank=True)
    tags = JSONField(blank=True, default=list)

    description = models.TextField(blank=True)

    subject_template = models.CharField(max_length=255, blank=True)
    template = models.TextField(blank=True)

    requires_foi = models.BooleanField(default=True)
    paused = models.BooleanField(default=False)

    search_url = models.CharField(max_length=1024, blank=True)

    provider = models.CharField(
        max_length=40,
        choices=settings.CAMPAIGN_PROVIDERS,
        blank=True
    )
    provider_kwargs = JSONField(default=dict, blank=True)

    objects = CampaignManager()

    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')

    def __str__(self):
        return self.title

    def get_description_template(self):
        if self.description:
            return Template(self.description)
        return Template('{{ title }}')

    def get_subject_template(self):
        if self.subject_template:
            return Template(self.subject_template)
        return Template('{{ title }}')

    def get_template(self):
        return Template(self.template)

    def get_provider(self):
        from froide_campaign.providers import get_provider

        return get_provider(self, self.provider, self.provider_kwargs)


class InformationObjectManager(models.Manager):

    SEARCH_LANG = 'simple'

    def get_search_vector(self):
        fields = [
            ('title', 'A'),
            ('search_text', 'A'),
        ]
        return functools.reduce(lambda a, b: a + b, [
            SearchVector(
                f, weight=w, config=self.SEARCH_LANG) for f, w in fields])

    def update_search_index(self, qs=None):
        if qs is None:
            qs = InformationObject.objects.all()
        for iobj in qs:
            iobj.search_text = iobj.get_search_text()
            iobj.save()
        search_vector = self.get_search_vector()
        InformationObject.objects.update(search_vector=search_vector)

    def search(self, qs, query):
        if query:
            query_search = SearchQuery(query, config=self.SEARCH_LANG)
            qs = qs.filter(
                Q(search_vector=query_search) |
                Q(title__contains=query) |
                Q(subtitle__contains=query))
        return qs

    def export_csv(self, queryset):
        fields = [
            "id", "campaign_id", "ident", "title",
            "slug", "publicbody_id", "foirequest_id",
            "foirequest__status", "foirequest__resolution",
            "foirequest__first_message", "resolved", "context_as_json",
            ('lat', lambda o: o.get_latitude()),
            ('lng', lambda o: o.get_longitude()),
        ]

        return export_csv(queryset, fields)


class InformationObject(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)

    ident = models.CharField(max_length=255)
    title = models.CharField(max_length=1000)
    subtitle = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255)
    ordering = models.CharField(max_length=255, blank=True)
    tags = JSONField(blank=True, default=list)

    context = JSONField(blank=True, default=dict)

    publicbody = models.ForeignKey(PublicBody, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    foirequest = models.ForeignKey(FoiRequest, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    foirequests = models.ManyToManyField(
        FoiRequest, blank=True, related_name='information_objects'
    )

    resolved = models.BooleanField(default=False)
    resolution_text = models.TextField(blank=True)
    resolution_link = models.CharField(max_length=255, blank=True)

    documents = models.ManyToManyField(FoiAttachment, blank=True)

    search_text = models.TextField(blank=True)
    search_vector = SearchVectorField(default='')

    address = models.TextField(_("Address"), blank=True)
    geo = gis_models.PointField(null=True, blank=True, geography=True)
    featured = models.BooleanField(default=False)

    objects = InformationObjectManager()

    class Meta:
        ordering = ('-ordering', 'title')
        verbose_name = _('Information object')
        verbose_name_plural = _('Information objects')

    def __str__(self):
        return self.title

    def get_context(self):
        return {
            'title': self.title,
            'ident': self.ident,
            'context': self.context,
            'publicbody': self.publicbody
        }

    @property
    def name(self):
        return self.title

    @property
    def context_as_json(self):
        return json.dumps(self.context)

    def get_description(self):
        template = self.campaign.get_description_template()
        context = Context(self.get_context())
        return mark_safe(template.render(context))

    def get_latitude(self):
        if self.geo:
            return self.geo.y

    def get_longitude(self):
        if self.geo:
            return self.geo.x

    def get_search_url(self):
        return self.campaign.search_url.format(
            title=urlquote(self.title),
            ident=urlquote(self.ident)
        )

    def get_search_text(self):
        return ' '.join([
            self.publicbody.name if self.publicbody else ''
            ] + [str(v) for v in self.context.values()]).strip()

    def make_request_url(self):
        provider = self.campaign.get_provider()
        return provider.get_request_url_with_object(self.ident, self)

    def get_froirequest_url(self):
        if self.get_best_foirequest():
            return self.get_best_foirequest().get_absolute_url()

    def get_best_foirequest(self):
        success = ['successful', 'partially_successful']
        withdrawn = ['user_withdrew_costs', 'user_withdrew']

        if self.foirequests.all():
            frs_success = self.foirequests.filter(resolution__in=success)
            if frs_success:
                return frs_success.first()
            frs_refused = self.foirequests.filter(resolution='refused')
            if frs_refused:
                return frs_refused.first()
            frs_withdrawn = self.foirequests.filter(resolution__in=withdrawn)
            if frs_withdrawn:
                return frs_withdrawn.first()
            return self.foirequests.all().first()

    def get_resolution(self):
        success = ['successful', 'partially_successful']
        withdrawn = ['user_withdrew_costs', 'user_withdrew']

        foirequest = self.get_best_foirequest()
        if foirequest:
            if foirequest.resolution in success:
                return 'successful'
            if foirequest.resolution == 'refused':
                return 'refused'
            if foirequest.resolution in withdrawn:
                return 'withdrawn'
            return 'pending'
        return 'normal'


class CampaignSubscription(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    email = models.EmailField()
