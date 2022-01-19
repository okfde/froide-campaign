import csv

from django.core.management.base import BaseCommand
from django.utils import translation
from django.conf import settings

from ...utils import CSVImporter


class Command(BaseCommand):
    help = "Loads a campaign's objects"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        filename = options["filename"]

        importer = CSVImporter()
        with open(filename) as f:
            reader = csv.DictReader(f)
            importer.run(reader)
