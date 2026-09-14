"""
Fetches live crypto prices and updates only the crypto symbols in the Stock table.
Faster than sync_stock_prices — run every 10 min for deposit modal accuracy.
Run via: python manage.py sync_crypto_rates
Suggested cron: every 10 minutes.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from app.models import Stock
from app.fmp_client import get_quotes

CRYPTO_SYMBOLS = [
    'BTCUSD', 'ETHUSD', 'BNBUSD', 'XRPUSD', 'SOLUSD',
    'ADAUSD', 'DOGEUSD', 'AVAXUSD', 'LINKUSD', 'LTCUSD',
]

SYMBOL_NAMES = {
    'BTCUSD': 'Bitcoin', 'ETHUSD': 'Ethereum', 'BNBUSD': 'BNB',
    'XRPUSD': 'XRP', 'SOLUSD': 'Solana', 'ADAUSD': 'Cardano',
    'DOGEUSD': 'Dogecoin', 'AVAXUSD': 'Avalanche',
    'LINKUSD': 'Chainlink', 'LTCUSD': 'Litecoin',
}


class Command(BaseCommand):
    help = 'Sync live FMP crypto prices into the Stock table'

    def handle(self, *args, **options):
        self.stdout.write(f'Fetching {len(CRYPTO_SYMBOLS)} crypto quotes...')
        quotes = get_quotes(CRYPTO_SYMBOLS)
        quote_map = {q['symbol'].upper(): q for q in quotes if 'symbol' in q}

        updated = skipped = 0
        for sym in CRYPTO_SYMBOLS:
            q = quote_map.get(sym, {})
            price = q.get('price')
            if not price:
                skipped += 1
                continue

            Stock.objects.update_or_create(
                symbol=sym,
                defaults={
                    'name': q.get('name') or SYMBOL_NAMES.get(sym, sym),
                    'price': Decimal(str(price)),
                    'change': Decimal(str(q.get('change') or 0)),
                    'change_percent': Decimal(str(
                        q.get('changePercentage') or q.get('changesPercentage') or 0
                    )),
                    'volume': int(q.get('volume') or 0),
                    'market_cap': int(q.get('marketCap') or 0),
                    'sector': 'crypto',
                    'logo_url': f'https://images.financialmodelingprep.com/symbol/{sym}.png',
                    'is_active': True,
                    'is_featured': sym in ('BTCUSD', 'ETHUSD'),
                },
            )
            updated += 1

        self.stdout.write(
            self.style.SUCCESS(f'Done — updated: {updated}, skipped: {skipped}')
        )
