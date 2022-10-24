from django.core.paginator import Paginator

POSTS_ON_PAGE: int = 10  # кол-во постов для отображения на странице


def paginations(request, posts):
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
