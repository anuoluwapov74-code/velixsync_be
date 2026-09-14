from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import News


@api_view(["GET"])
@permission_classes([AllowAny])
def list_news(request):
    """
    Get a paginated page of news articles with optional filtering by category and search.
    The full `content` body is intentionally omitted here (use news_detail for that) since
    the table holds thousands of rows and shipping full article bodies for every row on
    every page load is what made this endpoint hang.
    """
    # Get query parameters
    category = request.GET.get('category', '').strip()
    search_query = request.GET.get('search', '').strip()
    page = max(1, int(request.GET.get('page', 1) or 1))
    page_size = min(50, max(1, int(request.GET.get('page_size', 24) or 24)))

    # Start with all news, skipping the heavy content field we don't need for the list
    news_query = News.objects.only(
        'id', 'title', 'summary', 'category', 'source', 'author', 'published_at',
        'image', 'source_image_url', 'source_url', 'tags', 'is_featured', 'created_at', 'updated_at',
    ).order_by('-is_featured', '-published_at')

    # Apply category filter
    if category and category != 'All':
        news_query = news_query.filter(category=category)

    # Apply search filter
    if search_query:
        news_query = news_query.filter(
            title__icontains=search_query
        ) | news_query.filter(
            summary__icontains=search_query
        ) | news_query.filter(
            content__icontains=search_query
        )

    total = news_query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    offset = (page - 1) * page_size
    articles = news_query[offset:offset + page_size]

    # Serialize news articles
    news_list = []
    for article in articles:
        # Prefer an admin-uploaded Cloudinary image; fall back to the source's own image URL
        image_url = article.image.url if article.image else (article.source_image_url or None)

        news_list.append({
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "category": article.category,
            "source": article.source,
            "author": article.author,
            "published_at": article.published_at.isoformat(),
            "image_url": image_url,
            "source_url": article.source_url,
            "tags": article.tags,
            "is_featured": article.is_featured,
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat(),
        })

    return Response({
        "results": news_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def news_detail(request, news_id):
    """
    Get detailed information about a specific news article
    """
    try:
        article = News.objects.get(id=news_id)
    except News.DoesNotExist:
        return Response({
            "success": False,
            "error": "News article not found"
        }, status=404)

    # Prefer an admin-uploaded Cloudinary image; fall back to the source's own image URL
    image_url = article.image.url if article.image else (article.source_image_url or None)

    return Response({
        "success": True,
        "article": {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "content": article.content,
            "category": article.category,
            "source": article.source,
            "author": article.author,
            "published_at": article.published_at.isoformat(),
            "image_url": image_url,
            "source_url": article.source_url,
            "tags": article.tags,
            "is_featured": article.is_featured,
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat(),
        }
    })
