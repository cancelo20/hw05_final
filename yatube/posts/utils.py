from django.core.paginator import Paginator
from .constants import POSTS_LIMIT


def paginator_page(request, posts):
    paginator = Paginator(posts, POSTS_LIMIT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj
