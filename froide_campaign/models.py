# -*- encoding: utf-8 -*-
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.template import Template, Context

from jsonfield import JSONField

from froide.publicbody.models import PublicBody
from froide.foirequest.models import FoiRequest, FoiAttachment


@python_2_unicode_compatible
class Campaign(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    description = models.TextField(blank=True)

    template = models.TextField(blank=True)

    def __str__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('campaign-page', (), {'campaign_slug': self.slug})

    def get_template(self):
        return Template(self.template)


@python_2_unicode_compatible
class InformationObject(models.Model):
    campaign = models.ForeignKey(Campaign)

    ident = models.CharField(max_length=255)
    title = models.CharField(max_length=1000)
    slug = models.SlugField()
    ordering = models.CharField(max_length=255, blank=True)

    context = JSONField(blank=True)

    publicbody = models.ForeignKey(PublicBody, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    foirequest = models.ForeignKey(FoiRequest, null=True, blank=True,
                                    on_delete=models.SET_NULL)

    documents = models.ManyToManyField(FoiAttachment, blank=True)

    class Meta:
        ordering = ('-ordering',)

    def __str__(self):
        return self.title

    def make_request_url(self):
        if self.publicbody is None:
            return None
        pb_slug = self.publicbody.slug
        url = reverse('foirequest-make_request', kwargs={'public_body': pb_slug})
        subject = u'%s – %s' % (self.ident, self.title)
        if len(subject) > 250:
            subject = subject[:250] + '...'
        query = urlencode({
            'subject': subject.encode('utf-8'),
            'body': self.campaign.get_template().render(Context({
                'title': self.title,
                'ident': self.ident,
                'context': self.context
                })).encode('utf-8'),
            'ref': ('campaign:%s@%s' % (self.campaign.pk, self.slug)).encode('utf-8')
        })
        return '%s?%s' % (url, query)
