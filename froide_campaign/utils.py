import json
import logging

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.base import ContentFile
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string

from froide.foirequest.models import FoiRequest
from froide.publicbody.models import PublicBody

from .models import Campaign, CampaignCategory, InformationObject

logger = logging.getLogger()


class CSVImporter(object):
    def __init__(self, request):
        self.request = request
        self.pb_cache = {}
        self.campaign_cache = {}

    def run(self, reader):
        for line in reader:
            self.import_csv_line(line)

    def add_translations(self, iobj, line):
        translated_fields = ["title", "subtitle"]
        side_id = get_current_site(self.request).id
        languages = [
            lang.get("code") for lang in settings.PARLER_LANGUAGES.get(side_id)
        ]
        for lang in languages:
            iobj.set_current_language(lang)
            for field in translated_fields:
                field_name = "{}_{}".format(field, lang)
                if field_name in line:
                    value = line.pop(field_name)
                    setattr(iobj, field, value)
        iobj.save()

    def add_categories(self, iobj, line):
        if "categories" in line:
            categories = line.get("categories")
            iobj.categories.clear()
            if categories:
                cats_with_slug = [(slugify(cat), cat) for cat in categories.split(",")]
                for cat_tuple in cats_with_slug:
                    try:
                        cat = CampaignCategory.objects.get(
                            translations__slug=cat_tuple[0]
                        )
                    except CampaignCategory.DoesNotExist:
                        cat = CampaignCategory.objects.create(
                            title=cat_tuple[1], slug=cat_tuple[0]
                        )
                    iobj.categories.add(cat)

    def import_csv_line(self, line):
        # remove export columns
        line = {k: v for k, v in line.items() if not k.startswith("foirequest__")}
        line.pop("resolved", None)

        if "campaign" in line:
            campaign_slug = line.pop("campaign")
            if campaign_slug not in self.campaign_cache:
                campaign = Campaign.objects.get(slug=campaign_slug)
                self.campaign_cache[campaign_slug] = campaign
            campaign = self.campaign_cache[campaign_slug]
        else:
            campaign_id = line.pop("campaign_id")
            if campaign_id not in self.campaign_cache:
                campaign = Campaign.objects.get(id=campaign_id)
                self.campaign_cache[campaign_id] = campaign
            campaign = self.campaign_cache[campaign_id]

        title = line.pop("title")
        slug = line.pop("slug", "")
        if not slug:
            slug = slugify(title)
        slug = slug[:255]

        lookup = {}
        if line.get("id"):
            lookup = {"id": int(line.pop("id"))}
            ident = line.pop("ident")
        elif line.get("ident"):
            ident = line.pop("ident")
            lookup = {"ident": ident}
        else:
            ident = slug[:255]
            lookup = {"slug": slug}

        iobj = None
        try:
            iobj = InformationObject.objects.get(campaign=campaign, **lookup)
            logger.debug("Found %s" % slug)
        except InformationObject.DoesNotExist:
            pass

        pb = None
        if line.get("publicbody_id"):
            pb_id = line.pop("publicbody_id")
            if pb_id not in self.pb_cache:
                try:
                    self.pb_cache[pb_id] = PublicBody.objects.get(id=pb_id)
                except PublicBody.DoesNotExist:
                    pass
            pb = self.pb_cache[pb_id]

        foirequest = None
        if line.get("foirequest_id"):
            fr_id = line.pop("foirequest_id")
            try:
                foirequest = FoiRequest.objects.get(id=fr_id)
            except FoiRequest.DoesNotExist:
                pass
        ordering = line.pop("ordering", "")
        point = None

        if line.get("lat") and line.get("lng"):
            try:
                lat = float(line.pop("lat"))
                lng = float(line.pop("lng"))
                point = Point(lng, lat)
            except ValueError:
                pass

        subtitle = ""
        if "subtitle" in line:
            subtitle = line.pop("subtitle")

        featured = False
        if "featured" in line:
            featured = bool(line.pop("featured"))

        if line.get("context_as_json"):
            context = line.pop("context_as_json")
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
            iobj.featured = featured
            if foirequest:
                iobj.foirequest = foirequest
                iobj.foirequests.add(foirequest)
            iobj.save()

            self.add_translations(iobj, line)
            self.add_categories(iobj, line)

            return iobj

        iobj = InformationObject.objects.create(
            campaign=campaign,
            title=title,
            subtitle=subtitle,
            slug=slug,
            publicbody=pb,
            ident=ident,
            ordering=ordering,
            context=context_json,
            featured=featured,
            geo=point,
            foirequest=foirequest,
        )
        if foirequest:
            iobj.foirequests.add(foirequest)
        self.add_translations(iobj, line)
        self.add_categories(iobj, line)
        return iobj


def make_embed(embed_file, template, context):
    context.update({"build": True, "SITE_URL": settings.SITE_URL})
    output = render_to_string(template, context=context)
    embed_file.save("embed.html", ContentFile(output))
