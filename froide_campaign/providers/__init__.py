import importlib

from django.conf import settings

from .informationobject import InformationObjectProvider

PROVIDER_CLASS_CACHE = {}


def get_provider_class(dotted):
    module, klass = dotted.rsplit(".", 1)
    module = importlib.import_module(module)
    return getattr(module, klass)


def get_provider(campaign, provider_name, provider_kwargs):
    if provider_name in PROVIDER_CLASS_CACHE:
        provider_klass = PROVIDER_CLASS_CACHE[provider_name]
    else:
        provider_dict = dict(settings.CAMPAIGN_PROVIDERS)
        provider_class_path = provider_dict.get(provider_name)
        if provider_class_path is None:
            provider_klass = InformationObjectProvider
        else:
            provider_klass = get_provider_class(provider_class_path)
    return provider_klass(campaign, **provider_kwargs)
