import logging

from django.template.defaultfilters import slugify

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
        campaign_slug = line.pop('campaign')
        if campaign_slug not in self.campaign_cache:
            self.campaign_cache[campaign_slug] = Campaign.objects.get(slug=campaign_slug)
        campaign = self.campaign_cache[campaign_slug]

        title = line.pop('title')
        slug = line.pop('slug', slugify(title))
        slug = slug[:255]
        iobj = None
        try:
            iobj = InformationObject.objects.get(campaign=campaign, slug=slug)
            logger.debug('Found %s' % slug)
        except InformationObject.DoesNotExist:
            pass
        lookup = None
        lookup_val = None
        if 'public_body_id' in line:
            lookup_val = line.pop('public_body_id')
            lookup = {'id': lookup_val}
        if 'public_body' in line:
            lookup_val = line.pop('public_body')
            lookup = {'slug': lookup_val}
        if lookup_val is None:
            raise ValueError('Lookup not found')
        if lookup_val not in self.pb_cache:
            self.pb_cache[lookup_val] = PublicBody.objects.get(**lookup)
        pb = self.pb_cache[lookup_val]
        ordering = line.pop('ordering', '')
        if iobj is not None:
            iobj.slug = slug
            iobj.ident = slug[:255]
            iobj.ordering = ordering
            iobj.title = title
            iobj.context = line
            iobj.save()
            return iobj

        return InformationObject.objects.create(
            campaign=campaign,
            title=title,
            slug=slug[:50],
            publicbody=pb,
            ident=slug[:255],
            ordering=ordering,
            context=line
        )
