import logging

from django.core.files.base import ContentFile
from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.conf import settings

from froide.publicbody.models import PublicBody

from .models import Campaign, InformationObject

logger = logging.getLogger()


class CSVImporter(object):
    def __init__(self):
        self.pb_cache = {}
        self.campaign_cache = {}

    def run(self, reader):
        for line in reader:
            self.import_csv_line(line)

    def import_csv_line(self, line):
        if 'campaign' in line:
            campaign_slug = line.pop('campaign')
            if campaign_slug not in self.campaign_cache:
                campaign = Campaign.objects.get(slug=campaign_slug)
                self.campaign_cache[campaign_slug] = campaign
            campaign = self.campaign_cache[campaign_slug]
        else:
            campaign_id = line.pop('campaign_id')
            if campaign_id not in self.campaign_cache:
                campaign = Campaign.objects.get(id=campaign_id)
                self.campaign_cache[campaign_id] = campaign
            campaign = self.campaign_cache[campaign_id]

        title = line.pop('title')
        slug = line.pop('slug', slugify(title))
        slug = slug[:255]
        iobj = None
        try:
            iobj = InformationObject.objects.get(campaign=campaign, slug=slug)
            logger.debug('Found %s' % slug)
        except InformationObject.DoesNotExist:
            pass
        pb = None
        if 'publicbody_id' in line:
            pb_id = line.pop('publicbody_id')
            if pb_id:
                if pb_id not in self.pb_cache:
                    self.pb_cache[pb_id] = PublicBody.objects.get(
                        id=pb_id
                    )
                pb = self.pb_cache[pb_id]
        ordering = line.pop('ordering', '')
        if iobj is not None:
            iobj.slug = slug
            iobj.ident = slug[:255]
            iobj.ordering = ordering
            iobj.title = title
            iobj.context = line
            iobj.save()
            return iobj

        point = None
        if 'lat' in line and 'lng' in line:
            lat = float(line.pop('lat'))
            lng = float(line.pop('lng'))
            point = Point(lat, lng)

        return InformationObject.objects.create(
            campaign=campaign,
            title=title,
            slug=slug[:50],
            publicbody=pb,
            ident=slug[:255],
            ordering=ordering,
            context=line,
            geo=point
        )


def make_embed(embed_file, template, context):
    context.update({
        'build': True,
        'SITE_URL': settings.SITE_URL
    })
    output = render_to_string(template, context=context)
    embed_file.save('embed.html', ContentFile(output))
