# Generated by Django 3.1.6 on 2021-02-08 14:31

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations


def forwards_func(apps, schema_editor):
    Campaign = apps.get_model("froide_campaign", "Campaign")
    CampaignTranslation = apps.get_model("froide_campaign", "CampaignTranslation")

    for obj in Campaign.objects.all():
        CampaignTranslation.objects.create(
            master_id=obj.pk,
            language_code=settings.LANGUAGE_CODE,
            title=obj._title,
            slug=obj._slug,
            description=obj._description,
            subject_template=obj._subject_template,
            template=obj._template,
        )


def backwards_func(apps, schema_editor):
    Campaign = apps.get_model("froide_campaign", "Campaign")
    CampaignTranslation = apps.get_model("froide_campaign", "CampaignTranslation")

    for obj in Campaign.objects.all():
        translation = _get_translation(obj, CampaignTranslation)
        obj._title = translation.title
        obj._slug = translation.slug
        obj._description = translation.description
        obj._subject_template = translation.subject_template
        obj._template = translation.template
        obj.save()  # Note this only calls Model.save()


def _get_translation(object, MyModelTranslation):
    translations = MyModelTranslation.objects.filter(master_id=object.pk)
    try:
        # Try default translation
        return translations.get(language_code=settings.LANGUAGE_CODE)
    except ObjectDoesNotExist:
        try:
            # Try default language
            return translations.get(language_code=settings.PARLER_DEFAULT_LANGUAGE_CODE)
        except ObjectDoesNotExist:
            # Maybe the object was translated only in a specific language?
            # Hope there is a single translation
            return translations.get()


class Migration(migrations.Migration):
    dependencies = [
        ("froide_campaign", "0041_auto_20210208_1530"),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
