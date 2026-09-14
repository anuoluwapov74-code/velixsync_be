"""
Syncs live FMP prices for the Dow Jones 30 constituents into the
TreemapStock table, powering the Markets > Treemap tab.
Run via: python manage.py sync_treemap_stocks
Suggested cron: every 15 minutes (same cadence as sync_stock_prices).
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from app.models import TreemapStock
from app.fmp_client import get_quotes

# Dow Jones Industrial Average constituents (30 tickers).
DOW_30_SYMBOLS = [
    'AAPL', 'AMGN', 'AMZN', 'AXP', 'BA', 'CAT', 'CRM', 'CSCO', 'CVX',
    'DIS', 'GS', 'HD', 'HON', 'IBM', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
    'MRK', 'MSFT', 'NKE', 'NVDA', 'PG', 'SHW', 'TRV', 'UNH', 'V', 'VZ',
    'WMT',
]


class Command(BaseCommand):
    help = 'Sync live FMP prices for the Dow Jones 30 into the TreemapStock table'

    def handle(self, *args, **options):
        self.stdout.write(f'Fetching quotes for {len(DOW_30_SYMBOLS)} Dow 30 symbols...')
        quotes = get_quotes(DOW_30_SYMBOLS)
        quote_map = {q['symbol'].upper(): q for q in quotes if 'symbol' in q}

        created = updated = skipped = 0
        for sym in DOW_30_SYMBOLS:
            q = quote_map.get(sym.upper(), {})
            price = q.get('price')
            if not price:
                skipped += 1
                continue

            defaults = {
                'name': q.get('name') or sym,
                'index': 'dow30',
                'price': Decimal(str(price)),
                'change_percent': Decimal(str(q.get('changePercentage') or q.get('changesPercentage') or 0)),
                'market_cap': int(q.get('marketCap') or 0),
            }

            obj, was_created = TreemapStock.objects.update_or_create(symbol=sym, defaults=defaults)
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Done — created: {created}, updated: {updated}, skipped (no price): {skipped}'
            )
        )
