# -*- encoding: utf-8 -*-
import re

from django.core.management.base import BaseCommand
from django.utils import translation
from django.conf import settings

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
        InformationObject.objects.filter(campaign=campaign).delete()

        for line in reader:
            line['publicbody'] = 'deutscher-bundestag'
            title = line['titel']
            ident = line['ref']
            if not ident:
                continue
            context = {
                'cat': line['kat'],
                'year': line['jahr']
            }
            ordering = re.sub(r'(\d+)/(\d+)([A-Z]+\d*)', '\\2-\\1-\\3', ident)
            slug = ident.replace('/', '-').lower()
            try:
                InformationObject.objects.get(campaign=campaign, ident=ident)
                raise ValueError()
            except InformationObject.DoesNotExist:
                pass
            pb_slug = line['publicbody']
            if pb_slug not in pb_cache:
                pb_cache[pb_slug] = PublicBody.objects.get(slug=pb_slug)
            pb = pb_cache[pb_slug]
            InformationObject.objects.create(
                campaign=campaign,
                title=title,
                slug=slug,
                publicbody=pb,
                ident=ident,
                ordering=ordering,
                context=context
            )
            self.stdout.write((u"%s\n" % slug).encode('utf-8'))
