# -*- encoding: utf-8 -*-
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.template import Template, Context
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField

from froide.publicbody.models import PublicBody
from froide.foirequest.models import FoiRequest, FoiAttachment


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

    def get_subject_template(self):
        if self.subject_template:
            return Template(self.subject_template)
        return Template('{{ title }}')

    def get_template(self):
        return Template(self.template)


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

    documents = models.ManyToManyField(FoiAttachment, blank=True)

    class Meta:
        ordering = ('-ordering', 'title')
        verbose_name = _('Information object')
        verbose_name_plural = _('Information objects')

    def __str__(self):
        return self.title

    def get_search_url(self):
        return self.campaign.search_url.format(
            title=urlquote(self.title),
            ident=urlquote(self.ident)
        )

    def make_request_url(self):
        if self.publicbody is None:
            return None
        pb_slug = self.publicbody.slug
        context = Context({
            'title': self.title,
            'ident': self.ident,
            'context': self.context
        })
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
