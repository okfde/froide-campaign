# Generated by Django 3.1.4 on 2021-02-04 12:19

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations


def forwards_func(apps, schema_editor):
    InformationObject = apps.get_model("froide_campaign", "InformationObject")
    IObjectTranslation = apps.get_model(
        "froide_campaign", "InformationObjectTranslation"
    )

    for iobj in InformationObject.objects.all():
        IObjectTranslation.objects.create(
            master_id=iobj.pk,
            language_code=settings.LANGUAGE_CODE,
            title=iobj._title,
            subtitle=iobj._subtitle,
        )


def backwards_func(apps, schema_editor):
    InformationObject = apps.get_model("froide_campaign", "InformationObject")
    IObjectTranslation = apps.get_model(
        "froide_campaign", "InformationObjectTranslation"
    )

    for object in InformationObject.objects.all():
        translation = _get_translation(object, IObjectTranslation)
        object._title = translation.title
        object._subtitle = translation.subtitle
        object.save()


def _get_translation(object, InformationObjectTranslation):
    translations = InformationObjectTranslation.objects.filter(master_id=object.pk)
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
        ("froide_campaign", "0038_auto_20210204_1314"),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
