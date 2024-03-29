import functools
import json
import re
from urllib.parse import quote as urlquote

from django.apps import apps
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchVectorField
from django.db import models
from django.template import Context, Template
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from parler.managers import TranslatableManager
from parler.models import TranslatableModel, TranslatedFields

from froide.foirequest.models import FoiAttachment, FoiRequest
from froide.helper.csv_utils import export_csv
from froide.publicbody.models import PublicBody
from froide.team.models import Team

from froide_campaign.storage import OverwriteStorage

WORD_RE = re.compile(r"^\w+$", re.IGNORECASE)


def get_embed_path(instance, filename):
    return "campaign/page/embed/{0}/index.html".format(instance.slug)


class CampaignCategoryManager(TranslatableManager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("translations")


class CampaignCategory(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("title"), max_length=255),
        slug=models.SlugField(
            _("slug"),
            unique=False,
            max_length=255,
            help_text=_("Used to build the category's URL."),
        ),
        description=models.TextField(_("description"), blank=True),
    )

    objects = CampaignCategoryManager()

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self):
        return self.title


class CampaignPage(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    description = models.TextField(blank=True)
    public = models.BooleanField(default=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("User"),
    )
    team = models.ForeignKey(
        Team, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Team")
    )

    settings = models.JSONField(default=dict, blank=True)
    embed = models.FileField(
        blank=True, upload_to=get_embed_path, storage=OverwriteStorage()
    )

    campaigns = models.ManyToManyField("Campaign")

    class Meta:
        verbose_name = _("Campaign page")
        verbose_name_plural = _("Campaign pages")
        permissions = (("can_use_campaigns", _("Can use campaigns")),)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("campaign-page", kwargs={"slug": self.slug})

    def get_absolute_domain_embed_url(self):
        return settings.SITE_URL + reverse("campaign-embed", kwargs={"slug": self.slug})

    def get_edit_iframe(self, url=None):
        if url is None:
            url = self.get_absolute_domain_embed_url()
        return format_html(
            '<iframe src="{}" class="froide-campaign" '
            'id="froide-campaign-{}" style="width:100%;border:0" '
            'frameborder="0"></iframe>',
            url,
            str(self.id),
        )

    def get_embed_iframe(self):
        if not self.embed:
            return ""
        url = self.embed.url
        if not url.startswith("http"):
            url = settings.SITE_URL + url
        return self.get_edit_iframe(url)

    @property
    def requires_foi(self):
        return all(c.requires_foi for c in self.campaigns.all())

    def is_public(self):
        # necessary for auth can_read_object
        return self.public


class CampaignManager(TranslatableManager):
    def get_public(self):
        return self.filter(public=True)


class Campaign(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=255),
        slug=models.SlugField(),
        description=models.TextField(blank=True),
        subject_template=models.CharField(max_length=255, blank=True),
        template=models.TextField(blank=True),
    )

    public = models.BooleanField(default=False)

    category = models.CharField(max_length=255, blank=True)

    categories = models.ManyToManyField(
        CampaignCategory,
        related_name="campaigns",
        blank=True,
        verbose_name=_("categories"),
    )

    requires_foi = models.BooleanField(default=True)
    paused = models.BooleanField(default=False)

    search_url = models.CharField(max_length=1024, blank=True)

    provider = models.CharField(
        max_length=40, choices=settings.CAMPAIGN_PROVIDERS, blank=True
    )
    provider_kwargs = models.JSONField(default=dict, blank=True)

    objects = CampaignManager()

    class Meta:
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

    def __str__(self):
        return self.title

    def get_description_template(self):
        if self.description:
            return Template(self.description)
        return Template("{{ title }}")

    def get_subject_template(self):
        if self.subject_template:
            return Template(self.subject_template)
        return Template("{{ title }}")

    def get_template(self):
        return Template(self.template)

    def get_provider(self):
        from froide_campaign.providers import get_provider

        return get_provider(self, self.provider, self.provider_kwargs)


class InformationObjectManager(TranslatableManager):
    SEARCH_LANG = "simple"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("translations")

    def get_search_vector(self):
        fields = [
            ("search_text", "A"),
        ]
        return functools.reduce(
            lambda a, b: a + b,
            [SearchVector(f, weight=w, config=self.SEARCH_LANG) for f, w in fields],
        )

    def update_search_index(self, qs=None):
        if qs is None:
            qs = InformationObject.objects.all()
        for iobj in qs:
            iobj.search_text = iobj.get_search_text()
            iobj.save()
        search_vector = self.get_search_vector()
        InformationObject.objects.update(search_vector=search_vector)

    def search(self, qs, query):
        if not query:
            return qs
        search_queries = []
        for q in query.split():
            if WORD_RE.match(q):
                sq = SearchQuery(
                    "{}:*".format(q), search_type="raw", config=self.SEARCH_LANG
                )
            else:
                sq = SearchQuery(q, search_type="plain", config=self.SEARCH_LANG)
            search_queries.append(sq)

        query_search = functools.reduce(lambda a, b: a & b, search_queries)
        qs = qs.filter(search_vector=query_search)
        return qs

    def export_csv(self, queryset):
        fields = [
            "id",
            "campaign_id",
            "ident",
            "title",
            "slug",
            "publicbody_id",
            "foirequest_id",
            "foirequest__status",
            "foirequest__resolution",
            "foirequest__created_at",
            "resolved",
            "context_as_json",
            ("lat", lambda o: o.get_latitude()),
            ("lng", lambda o: o.get_longitude()),
        ]

        return export_csv(queryset, fields)


class InformationObject(TranslatableModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)

    ident = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255)
    ordering = models.CharField(max_length=255, blank=True)

    translations = TranslatedFields(
        title=models.CharField(max_length=1000),
        subtitle=models.CharField(max_length=255, blank=True),
    )

    categories = models.ManyToManyField(
        CampaignCategory,
        related_name="information_objects",
        blank=True,
        verbose_name=_("categories"),
    )

    context = models.JSONField(blank=True, default=dict)

    publicbody = models.ForeignKey(
        PublicBody, null=True, blank=True, on_delete=models.SET_NULL
    )
    foirequest = models.ForeignKey(
        FoiRequest, null=True, blank=True, on_delete=models.SET_NULL
    )
    foirequests = models.ManyToManyField(
        FoiRequest, blank=True, related_name="information_objects"
    )

    resolved = models.BooleanField(default=False)
    resolution_text = models.TextField(blank=True)
    resolution_link = models.CharField(max_length=255, blank=True)

    documents = models.ManyToManyField(FoiAttachment, blank=True)

    search_text = models.TextField(blank=True)
    search_vector = SearchVectorField(default="", editable=False)

    address = models.TextField(_("Address"), blank=True)
    geo = gis_models.PointField(null=True, blank=True, geography=True)
    featured = models.BooleanField(default=False)

    objects = InformationObjectManager()

    class Meta:
        ordering = ("-ordering", "id")
        verbose_name = _("Information object")
        verbose_name_plural = _("Information objects")

    def __str__(self):
        return self.title

    def get_context(self, language=None):
        if language:
            self.set_current_language(language)
        return {
            "title": self.title,
            "ident": self.ident,
            "context": self.context,
            "publicbody": self.publicbody,
        }

    @property
    def name(self):
        return self.title

    @property
    def context_as_json(self):
        return json.dumps(self.context)

    def get_description(self):
        template = self.campaign.get_description_template()
        context = Context(self.get_context())
        return mark_safe(template.render(context))

    def get_latitude(self):
        if self.geo:
            return self.geo.y

    def get_longitude(self):
        if self.geo:
            return self.geo.x

    def get_search_url(self):
        return self.campaign.search_url.format(
            title=urlquote(self.title), ident=urlquote(self.ident)
        )

    def get_search_text(self):
        titles = " ".join(
            [translation.title for translation in self.translations.all()]
        )
        subtitles = " ".join(
            [translation.subtitle for translation in self.translations.all()]
        )
        cat_ids = self.categories.all().values_list("id", flat=True)
        CategoryTranslation = apps.get_model(
            "froide_campaign", "CampaignCategoryTranslation"
        )
        all_cats = CategoryTranslation.objects.filter(master__in=cat_ids).values_list(
            "title", flat=True
        )

        as_list = [cat for cat in all_cats]

        text = " ".join(
            [titles, subtitles, self.publicbody.name if self.publicbody else ""]
            + as_list
            + [str(v) for v in self.context.values()]
        ).strip()
        return text

    def make_request_url(self):
        provider = self.campaign.get_provider()
        return provider.get_request_url_redirect(self.ident)

    def get_best_foirequest(self):
        return self.foirequests.all().first()

    def get_public(self):
        foirequest = self.get_best_foirequest()
        if foirequest:
            return foirequest.visibility == FoiRequest.VISIBILITY.VISIBLE_TO_PUBLIC
        return True

    def get_resolution(self):
        success = ["successful", "partially_successful"]
        withdrawn = ["user_withdrew_costs", "user_withdrew"]

        foirequest = self.get_best_foirequest()
        if foirequest:
            if foirequest.resolution in success:
                return "successful"
            if foirequest.resolution == "refused":
                return "refused"
            if foirequest.resolution in withdrawn:
                return "withdrawn"
            return "pending"
        return "normal"


class CampaignSubscription(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    email = models.EmailField()
