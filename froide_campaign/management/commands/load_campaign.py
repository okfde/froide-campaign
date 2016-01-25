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

        for line in reader:
            line['publicbody'] = 'deutscher-bundestag'
            title = line['Titel']
            ident = line['Aktenzeichen']
            ordering = re.sub(r'^(.*) - (\d+)/(\d+)$', '\\3-\\2-\\1', line['Aktenzeichen'])
            ordering = ordering.replace(' ', '')
            context = {
                'year': line['Jahr'],
                'status': line['Status'],
                'abteilung': line['Abteilung']
            }
            slug = line['ID'].replace('/', '-').replace(' ', '-').lower()
            try:
                iobj = InformationObject.objects.get(campaign=campaign, ordering=ordering)
            except InformationObject.DoesNotExist:
                print('Not found %s' % ordering)
                continue
            pb_slug = line['publicbody']
            if pb_slug not in pb_cache:
                pb_cache[pb_slug] = PublicBody.objects.get(slug=pb_slug)
            pb = pb_cache[pb_slug]
            if iobj is not None:
                iobj.slug = slug
                iobj.ordering = ordering
                iobj.ident = ident
                iobj.title = title
                iobj.context = context
                iobj.save()
                continue

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
