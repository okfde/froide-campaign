# -*- encoding: utf-8 -*-
import re

from django.core.management.base import BaseCommand
from django.utils import translation
from django.conf import settings
from django.template.defaultfilters import slugify

import unicodecsv

from froide.publicbody.models import PublicBody

from ...models import Campaign, InformationObject


class Command(BaseCommand):
    help = "Loads a campaign's objects"

    def add_arguments(self, parser):
        parser.add_argument('campaign', type=str)
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        campaign_slug = options['campaign']
        campaign = Campaign.objects.get(slug=campaign_slug)

        filename = options['filename']

        pb_cache = {}

        reader = unicodecsv.DictReader(open(filename))

        for line in reader:
            title = line.pop('title')
            slug = line.pop('slug', slugify(title))
            iobj = None
            try:
                iobj = InformationObject.objects.get(campaign=campaign, slug=slug)
                print('Found %s' % slug)
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
            if lookup_val not in pb_cache:
                pb_cache[lookup_val] = PublicBody.objects.get(**lookup)
            pb = pb_cache[lookup_val]
            ordering = line.pop('ordering', '')
            if iobj is not None:
                iobj.slug = slug[:50]
                iobj.ident = slug[:255]
                iobj.ordering = ordering
                iobj.title = title
                iobj.context = line
                iobj.save()
                continue

            InformationObject.objects.create(
                campaign=campaign,
                title=title,
                slug=slug[:50],
                publicbody=pb,
                ident=slug[:255],
                ordering=ordering,
                context=line
            )
            self.stdout.write((u"%s\n" % slug).encode('utf-8'))
