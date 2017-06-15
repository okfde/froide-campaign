# -*- encoding: utf-8 -*-
import functools
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.encoding import python_2_unicode_compatible
from django.template import Template, Context
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.search import (SearchVectorField, SearchVector,
        SearchVectorExact, SearchQuery)

from froide.publicbody.models import PublicBody
from froide.foirequest.models import FoiRequest, FoiAttachment


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
        rhs, rhs_params = super(SearchVectorExact, self).process_rhs(qn, connection)
        rhs = '(to_tsquery(%s::regconfig, %s))'
        rhs_params[1] = ' & '.join('%s:*' % s for s in rhs_params[1].split())
        return rhs, rhs_params

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s @@ %s' % (lhs, rhs), params


SearchVectorField.register_lookup(SearchVectorStartsWith)


@python_2_unicode_compatible
class CampaignPage(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    description = models.TextField(blank=True)
    public = models.BooleanField(default=False)

    campaigns = models.ManyToManyField('Campaign')

    class Meta:
        verbose_name = _('Campaign page')
        verbose_name_plural = _('Campaign pages')

    def __str__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('campaign-page', (), {'slug': self.slug})

    @property
    def requires_foi(self):
        return all(c.requires_foi for c in self.campaigns.all())


@python_2_unicode_compatible
class Campaign(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    public = models.BooleanField(default=False)

    category = models.CharField(max_length=255, blank=True)

    description = models.TextField(blank=True)

    subject_template = models.CharField(max_length=255, blank=True)
    template = models.TextField(blank=True)

    requires_foi = models.BooleanField(default=True)
    search_url = models.CharField(max_length=1024, blank=True)

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


class InformationObjectManager(models.Manager):

    SEARCH_LANG = 'simple'

    def get_search_vector(self):
        fields = [
            ('title', 'A'),
            ('search_text', 'A'),
        ]
        return functools.reduce(lambda a, b: a + b,
            [SearchVector(f, weight=w, config=self.SEARCH_LANG) for f, w in fields])

    def update_search_index(self):
        for iobj in InformationObject.objects.all():
            iobj.search_text = iobj.get_search_text()
            iobj.save()

        InformationObject.objects.update(search_vector=self.get_search_vector())

    def search(self, qs, query):
        if query:
            query = SearchQuery(query, config=self.SEARCH_LANG)
            qs = qs.filter(search_vector__startswith=query)
        return qs


@python_2_unicode_compatible
class InformationObject(models.Model):
    campaign = models.ForeignKey(Campaign)

    ident = models.CharField(max_length=255)
    title = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=255)
    ordering = models.CharField(max_length=255, blank=True)

    context = JSONField(blank=True)

    publicbody = models.ForeignKey(PublicBody, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    foirequest = models.ForeignKey(FoiRequest, null=True, blank=True,
                                    on_delete=models.SET_NULL)

    resolved = models.BooleanField(default=False)
    resolution_text = models.TextField(blank=True)
    resolution_link = models.CharField(max_length=255, blank=True)

    documents = models.ManyToManyField(FoiAttachment, blank=True)

    search_text = models.TextField(blank=True)
    search_vector = SearchVectorField(default='')

    objects = InformationObjectManager()

    class Meta:
        ordering = ('-ordering', 'title')
        verbose_name = _('Information object')
        verbose_name_plural = _('Information objects')

    def __str__(self):
        return self.title

    def get_context(self):
        return Context({
            'title': self.title,
            'ident': self.ident,
            'context': self.context,
            'publicbody': self.publicbody
        })

    def get_description(self):
        template = self.campaign.get_description_template()
        context = self.get_context()
        return mark_safe(template.render(context))

    def get_search_url(self):
        return self.campaign.search_url.format(
            title=urlquote(self.title),
            ident=urlquote(self.ident)
        )

    def get_search_text(self):
        return ' '.join([self.publicbody.name] + list(self.context.values()))

    def make_request_url(self):
        if self.publicbody is None:
            return None
        pb_slug = self.publicbody.slug
        context = self.get_context()
        url = reverse('foirequest-make_request', kwargs={'public_body': pb_slug})
        subject = self.campaign.get_subject_template().render(context)
        if len(subject) > 250:
            subject = subject[:250] + '...'
        query = urlencode({
            'subject': subject.encode('utf-8'),
            'body': self.campaign.get_template().render(context).encode('utf-8'),
            'ref': ('campaign:%s@%s' % (self.campaign.pk, self.pk)).encode('utf-8')
        })
        return '%s?%s' % (url, query)
