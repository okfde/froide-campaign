from .models import Campaign


def connect_info_object(sender, **kwargs):
    reference = kwargs.get('reference')
    if not reference:
        return
    if not reference.startswith('campaign:'):
        return
    namespace, campaign_value = reference.split(':', 1)
    try:
        campaign, ident = campaign_value.split('@', 1)
    except (ValueError, IndexError):
        return

    try:
        campaign_pk = int(campaign)
    except ValueError:
        return

    try:
        campaign = Campaign.objects.get(pk=campaign_pk)
    except Campaign.DoesNotExist:
        return

    provider = campaign.get_provider()
    provider.connect_request(ident, sender)
