# Generated by Django 3.0.8 on 2020-08-23 11:02

from django.db import migrations


def fill_foirequests_field(apps, schema_editor):
    InformationObject = apps.get_model("froide_campaign", "InformationObject")
    for information_object in InformationObject.objects.all():
        request = information_object.foirequest
        if request:
            information_object.foirequests.add(request)


class Migration(migrations.Migration):

    dependencies = [
        ("froide_campaign", "0022_informationobject_foirequests"),
    ]

    operations = [migrations.RunPython(fill_foirequests_field)]
