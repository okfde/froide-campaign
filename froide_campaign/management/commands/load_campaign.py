# -*- encoding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import translation
from django.conf import settings

import unicodecsv

from ...utils import CSVImporter


class Command(BaseCommand):
    help = "Loads a campaign's objects"

    def add_arguments(self, parser):
        parser.add_argument('campaign', type=str)
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        filename = options['filename']

        reader = unicodecsv.DictReader(open(filename, 'rb'))
        importer = CSVImporter()
        importer.run(reader)
