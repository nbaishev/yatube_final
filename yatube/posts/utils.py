from django.conf import settings
from django.core.paginator import Paginator


def paginator(request, post_list):
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return page_obj
