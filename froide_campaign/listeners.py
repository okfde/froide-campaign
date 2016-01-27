from .models import Campaign, InformationObject


def connect_info_object(sender, **kwargs):
    reference = kwargs.get('reference')
    if not reference:
        return
    if not reference.startswith('campaign:'):
        return
    namespace, campaign_value = reference.split(':', 1)
    try:
        campaign, slug = campaign_value.split('@', 1)
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

    try:
        iobj = InformationObject.objects.get(campaign=campaign, slug=slug)
    except InformationObject.DoesNotExist:
        return

    if iobj.foirequest is not None:
        return

    if iobj.publicbody != sender.public_body:
        return

    if not sender.public:
        return

    iobj.foirequest = sender
    iobj.save()
