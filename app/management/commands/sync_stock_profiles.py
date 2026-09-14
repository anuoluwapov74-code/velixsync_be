"""
Syncs slower-moving company metadata (sector, description, domain/logo
fallback, 52-week range, beta, average volume, dividend yield) for curated
stock symbols into the Stock table.
Run via: python manage.py sync_stock_profiles
Suggested cron: once daily (this data barely changes intraday).
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from app.models import Stock
from app.fmp_client import get_profile, get_ratios_ttm
from .sync_stock_prices import CATEGORY_SYMBOLS

# FMP's raw sector strings collapsed onto the six filter pills the Stocks tab shows.
SECTOR_NORM = {
    "Financial Services": "Finance",
    "Consumer Cyclical": "Consumer",
    "Consumer Defensive": "Consumer",
    "Communication Services": "Technology",
}


def _normalize_sector(sector):
    return SECTOR_NORM.get(sector, sector)


def _domain_from_url(url):
    if not url:
        return ""
    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def _parse_52w_range(range_str):
    """FMP returns '225.95-344.57' style strings."""
    if not range_str or "-" not in range_str:
        return None, None
    try:
        low_str, high_str = range_str.split("-", 1)
        return Decimal(low_str.strip()), Decimal(high_str.strip())
    except (InvalidOperation, ValueError):
        return None, None


def _fetch_one(symbol):
    return symbol, get_profile(symbol), get_ratios_ttm(symbol)


class Command(BaseCommand):
    help = 'Sync daily company profile metadata (sector, description, 52w range, beta, avg volume, dividend) for curated stocks'

    def handle(self, *args, **options):
        symbols = CATEGORY_SYMBOLS.get('stock', [])
        self.stdout.write(f'Fetching profiles for {len(symbols)} stock symbols...')

        updated = skipped = 0
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(_fetch_one, sym) for sym in symbols]
            for future in as_completed(futures):
                symbol, profile, ratios = future.result()
                if not profile:
                    skipped += 1
                    continue

                low_52w, high_52w = _parse_52w_range(profile.get("range"))
                price = profile.get("price") or 0
                last_dividend = profile.get("lastDividend") or 0
                div_yield = (Decimal(str(last_dividend)) / Decimal(str(price)) * 100) if price and last_dividend else Decimal("0")

                pe_ratio = ratios.get("priceToEarningsRatioTTM")
                eps_ttm = ratios.get("netIncomePerShareTTM")

                updated_count = Stock.objects.filter(symbol=symbol).update(
                    sector=_normalize_sector(profile.get("sector") or "") or None,
                    exchange=profile.get("exchange") or "",
                    domain=_domain_from_url(profile.get("website")),
                    description=profile.get("description") or "",
                    high_52w=high_52w if high_52w is not None else Decimal("0"),
                    low_52w=low_52w if low_52w is not None else Decimal("0"),
                    beta=Decimal(str(profile.get("beta") or 0)),
                    avg_volume=int(profile.get("averageVolume") or 0),
                    div_yield=div_yield,
                    pe=Decimal(str(pe_ratio)) if pe_ratio is not None else None,
                    eps=Decimal(str(eps_ttm)) if eps_ttm is not None else Decimal("0"),
                )
                if updated_count:
                    updated += 1
                else:
                    skipped += 1  # symbol not yet synced by sync_stock_prices

        self.stdout.write(
            self.style.SUCCESS(f'Done — updated: {updated}, skipped: {skipped}')
        )
