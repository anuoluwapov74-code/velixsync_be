"""
Fetches fresh news from FMP (stock + crypto feeds) and saves new articles to DB.
Run via: python manage.py fetch_fmp_news
Suggested cron: every hour.
"""
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.utils.timezone import make_aware, is_naive
from app.models import News
from app.fmp_client import get_news


class Command(BaseCommand):
    help = 'Fetch FMP news (stock + crypto) and save new articles to the News table'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=20,
                            help='Articles to fetch per feed (default 20)')

    def handle(self, *args, **options):
        limit = options['limit']
        feeds = [('stock', 'Stocks'), ('crypto', 'Cryptocurrency')]
        created_total = skipped_total = 0

        for feed_type, category_label in feeds:
            self.stdout.write(f'Fetching {feed_type} news (limit={limit})...')
            try:
                articles = get_news(feed_type, limit=limit)
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f'  FMP error for {feed_type}: {exc}'))
                continue

            for a in articles:
                title = (a.get('title') or '').strip()
                if not title:
                    skipped_total += 1
                    continue

                if News.objects.filter(title=title).exists():
                    skipped_total += 1
                    continue

                pub_dt = None
                raw_date = a.get('publishedDate') or a.get('date')
                if raw_date:
                    try:
                        pub_dt = parse_datetime(raw_date)
                        if pub_dt is not None and is_naive(pub_dt):
                            pub_dt = make_aware(pub_dt)
                    except Exception:
                        pass
                if pub_dt is None:
                    pub_dt = timezone.now()

                symbol = (a.get('symbol') or '').strip()
                News.objects.create(
                    title=title,
                    summary=(a.get('text') or '')[:500],
                    content=a.get('text') or '',
                    category=category_label,
                    source=a.get('site') or a.get('publisher') or 'FMP',
                    author=a.get('publisher') or 'Market News',
                    published_at=pub_dt,
                    tags=[symbol] if symbol else [],
                    is_featured=False,
                    source_image_url=a.get('image') or None,
                    source_url=a.get('url') or None,
                )
                created_total += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Done — created: {created_total}, skipped (duplicate/empty): {skipped_total}'
            )
        )
