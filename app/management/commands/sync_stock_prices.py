"""
Syncs live FMP prices for all curated symbols into the Stock DB table.
Run via: python manage.py sync_stock_prices
Suggested cron: every 15 minutes.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from app.models import Stock
from app.fmp_client import get_quotes

CATEGORY_SYMBOLS = {
    'stock': [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META',
        'JPM', 'V', 'JNJ', 'WMT', 'MA', 'PG', 'UNH', 'BAC',
        'XOM', 'AVGO', 'LLY', 'NFLX', 'DIS',
    ],
    'crypto': [
        'BTCUSD', 'ETHUSD', 'BNBUSD', 'XRPUSD', 'SOLUSD',
        'ADAUSD', 'DOGEUSD', 'AVAXUSD', 'LINKUSD', 'LTCUSD',
    ],
    'etf': [
        'SPY', 'QQQ', 'IWM', 'DIA', 'GLD', 'VTI', 'VOO',
        'ARKK', 'XLF', 'XLK', 'TLT', 'EFA', 'SLV', 'XLE', 'VNQ',
    ],
    'indices': ['SPX', 'NDX', 'DJI', 'RUT', 'VIX'],
}

SYMBOL_NAMES = {
    'BTCUSD': 'Bitcoin', 'ETHUSD': 'Ethereum', 'BNBUSD': 'BNB',
    'XRPUSD': 'XRP', 'SOLUSD': 'Solana', 'ADAUSD': 'Cardano',
    'DOGEUSD': 'Dogecoin', 'AVAXUSD': 'Avalanche',
    'LINKUSD': 'Chainlink', 'LTCUSD': 'Litecoin',
    'SPX': 'S&P 500', 'NDX': 'NASDAQ 100', 'DJI': 'Dow Jones',
    'RUT': 'Russell 2000', 'VIX': 'CBOE VIX',
}

FEATURED = {'AAPL', 'MSFT', 'BTCUSD', 'ETHUSD', 'SPY', 'NVDA'}


class Command(BaseCommand):
    help = 'Sync live FMP prices for curated symbols into the Stock table'

    def handle(self, *args, **options):
        all_symbols = [s for syms in CATEGORY_SYMBOLS.values() for s in syms]
        sym_to_cat = {s: c for c, syms in CATEGORY_SYMBOLS.items() for s in syms}

        self.stdout.write(f'Fetching quotes for {len(all_symbols)} symbols...')
        quotes = get_quotes(all_symbols)
        quote_map = {q['symbol'].upper(): q for q in quotes if 'symbol' in q}

        created = updated = skipped = 0
        for sym in all_symbols:
            q = quote_map.get(sym.upper(), {})
            price = q.get('price')
            if not price:
                skipped += 1
                continue

            defaults = {
                'name': q.get('name') or SYMBOL_NAMES.get(sym, sym),
                'category': sym_to_cat.get(sym, 'stock'),
                'price': Decimal(str(price)),
                'change': Decimal(str(q.get('change') or 0)),
                'change_percent': Decimal(str(q.get('changePercentage') or q.get('changesPercentage') or 0)),
                'volume': int(q.get('volume') or 0),
                'market_cap': int(q.get('marketCap') or 0),
                'logo_url': f'https://images.financialmodelingprep.com/symbol/{sym}.png',
                'is_active': True,
                'is_featured': sym in FEATURED,
            }
            # Note: this endpoint's /quote response has no pe/eps fields on our
            # plan — those come from the daily sync_stock_profiles command
            # instead (via /ratios-ttm). Don't set them here or they'd get
            # clobbered back to null every 15 minutes.

            obj, was_created = Stock.objects.update_or_create(symbol=sym, defaults=defaults)
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Done — created: {created}, updated: {updated}, skipped (no price): {skipped}'
            )
        )
