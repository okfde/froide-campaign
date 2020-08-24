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
        kwargs = {
            'pk': int(slug)
        }
    except ValueError:
        kwargs = {'slug': slug}

    try:
        iobj = InformationObject.objects.get(campaign=campaign, **kwargs)
    except InformationObject.DoesNotExist:
        return

    if iobj.publicbody != sender.public_body:
        return

    if not sender.public:
        return

    if iobj.foirequest is None:
        iobj.foirequest = sender

    iobj.foirequests.add(sender)
    iobj.save()
