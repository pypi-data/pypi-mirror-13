from django import template
from django.core.cache import cache
from django.http import HttpRequest
from blocks.models import SiteBlock

register = template.Library()


@register.inclusion_tag('blocks/site_block.html')
def show_block(request, block_id):
    """

    :type request: django.http.HttpRequest
    :type block_id: str
    """
    res = {
        'id': None,
        'block_id': None,
        'text': None,
        'can_edit': False
    }

    if not request or not isinstance(request, HttpRequest):
        return res

    if request.user and request.user.has_perm('blocks.change_siteblock'):
        res['can_edit'] = True

    cache_prefix = block_id + '_' + request.path.replace('/', '_') + '_'

    cached_values = cache.get_many([cache_prefix + 'id', cache_prefix + 'text', ])

    if not cached_values:
        try:
            b = SiteBlock.objects.get(url=request.path, block_id=block_id)
        except SiteBlock.DoesNotExist:
            try:
                b = SiteBlock.objects.get(url='', block_id=block_id)
            except SiteBlock.DoesNotExist:
                return res

        res['id'] = b.id
        res['block_id'] = b.block_id
        res['text'] = b.text

        cache.set_many({ cache_prefix + 'id': b.id, cache_prefix + 'text': b.text })
    else:
        res['id'] = cached_values[cache_prefix + 'id']
        res['block_id'] = block_id
        res['text'] = cached_values[cache_prefix + 'text']

    return res
