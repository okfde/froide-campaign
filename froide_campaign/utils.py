import json
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

        lookup = {}
        if line.get('ident'):
            ident = line.pop('ident')
            lookup = {'ident': ident}
        else:
            ident = slug[:255]
            lookup = {'slug': slug}

        iobj = None
        try:
            iobj = InformationObject.objects.get(
                campaign=campaign, **lookup
            )
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
        point = None
        if 'lat' in line and 'lng' in line:
            try:
                lat = float(line.pop('lat'))
                lng = float(line.pop('lng'))
                point = Point(lng, lat)
            except ValueError:
                pass

        subtitle = ''
        if 'subtitle' in line:
            subtitle = line.pop('subtitle')

        tags = []
        if 'tags' in line:
            tags = line.pop('tags').split(',')

        featured = False
        if 'featured' in line:
            featured = bool(line.pop('featured'))

        if 'context' in line:
            context = line.pop('context')
            context_json = json.loads(context)
        else:
            context_json = line

        if iobj is not None:
            iobj.slug = slug
            iobj.ident = ident
            iobj.ordering = ordering
            iobj.publicbody = pb
            iobj.geo = point
            iobj.title = title
            iobj.subtitle = subtitle
            iobj.context = context_json
            iobj.tags = tags
            iobj.featured = featured
            iobj.save()
            return iobj
        return InformationObject.objects.create(
            campaign=campaign,
            title=title,
            subtitle=subtitle,
            slug=slug,
            publicbody=pb,
            ident=ident,
            ordering=ordering,
            context=context_json,
            tags=tags,
            featured=featured,
            geo=point
        )


def make_embed(embed_file, template, context):
    context.update({
        'build': True,
        'SITE_URL': settings.SITE_URL
    })
    output = render_to_string(template, context=context)
    embed_file.save('embed.html', ContentFile(output))
