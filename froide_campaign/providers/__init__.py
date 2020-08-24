import importlib

from django.conf import settings

from .base import BaseProvider


def get_provider_class(dotted):
    module, klass = dotted.rsplit('.', 1)
    module = importlib.import_module(module)
    return getattr(module, klass)


def get_provider(campaign, provider_name, provider_kwargs):
    provider_class_path = settings.CAMPAIGN_PROVIDERS.get(provider_name)
    if provider_class_path is None:
        provider_klass = BaseProvider
    else:
        provider_klass = get_provider_class(provider_class_path)
    return provider_klass(campaign, **provider_kwargs)
