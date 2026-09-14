"""
Syncs the last 20 real daily closing prices per curated stock symbol into
StockHistory, for the Stocks tab sparkline.
Run via: python manage.py sync_stock_history
Suggested cron: once daily (after market close).
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from app.models import StockHistory
from app.fmp_client import get_historical_prices
from .sync_stock_prices import CATEGORY_SYMBOLS

DAYS = 20


def _fetch_one(symbol):
    return symbol, get_historical_prices(symbol, days=DAYS)


class Command(BaseCommand):
    help = f'Sync the last {DAYS} daily closes per curated stock symbol into StockHistory (sparkline data)'

    def handle(self, *args, **options):
        symbols = CATEGORY_SYMBOLS.get('stock', [])
        self.stdout.write(f'Fetching {DAYS}-day history for {len(symbols)} stock symbols...')

        updated = skipped = 0
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(_fetch_one, sym) for sym in symbols]
            for future in as_completed(futures):
                symbol, prices = future.result()
                if not prices:
                    skipped += 1
                    continue
                StockHistory.objects.update_or_create(symbol=symbol, defaults={"prices": prices})
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(f'Done — updated: {updated}, skipped (no data): {skipped}')
        )
