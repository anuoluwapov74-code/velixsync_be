"""Random portfolio positions for traders (placeholder data until real positions are entered)."""

import random
from decimal import Decimal

FMP_LOGO_URL = "https://images.financialmodelingprep.com/symbol/{symbol}.png"

# Well-known tickers with logos on FMP. (symbol, company name)
STOCK_POOL = [
    ("AAPL", "Apple Inc."), ("MSFT", "Microsoft Corporation"), ("GOOGL", "Alphabet Inc."),
    ("AMZN", "Amazon.com, Inc."), ("NVDA", "NVIDIA Corporation"), ("META", "Meta Platforms, Inc."),
    ("TSLA", "Tesla, Inc."), ("NFLX", "Netflix, Inc."), ("AMD", "Advanced Micro Devices, Inc."),
    ("INTC", "Intel Corporation"), ("CRM", "Salesforce, Inc."), ("ORCL", "Oracle Corporation"),
    ("ADBE", "Adobe Inc."), ("CSCO", "Cisco Systems, Inc."), ("IBM", "International Business Machines"),
    ("JPM", "JPMorgan Chase & Co."), ("BAC", "Bank of America Corporation"), ("GS", "The Goldman Sachs Group, Inc."),
    ("V", "Visa Inc."), ("MA", "Mastercard Incorporated"), ("PYPL", "PayPal Holdings, Inc."),
    ("WMT", "Walmart Inc."), ("KO", "The Coca-Cola Company"), ("PEP", "PepsiCo, Inc."),
    ("PG", "The Procter & Gamble Company"), ("MCD", "McDonald's Corporation"), ("NKE", "NIKE, Inc."),
    ("SBUX", "Starbucks Corporation"), ("DIS", "The Walt Disney Company"), ("HD", "The Home Depot, Inc."),
    ("JNJ", "Johnson & Johnson"), ("PFE", "Pfizer Inc."), ("UNH", "UnitedHealth Group Incorporated"),
    ("MRK", "Merck & Co., Inc."), ("ABBV", "AbbVie Inc."), ("LLY", "Eli Lilly and Company"),
    ("XOM", "Exxon Mobil Corporation"), ("CVX", "Chevron Corporation"), ("BA", "The Boeing Company"),
    ("CAT", "Caterpillar Inc."), ("GE", "GE Aerospace"), ("HON", "Honeywell International Inc."),
    ("VZ", "Verizon Communications Inc."), ("T", "AT&T Inc."), ("COST", "Costco Wholesale Corporation"),
    ("UBER", "Uber Technologies, Inc."), ("PLTR", "Palantir Technologies Inc."), ("SHOP", "Shopify Inc."),
]


def generate_positions(count=None, rng=random):
    """Return a list of position dicts (market, name, logo_url, direction, invested, profit_loss, value)."""
    count = count or rng.randint(8, 12)
    picks = rng.sample(STOCK_POOL, min(count, len(STOCK_POOL)))

    positions = []
    for symbol, name in picks:
        invested = Decimal(str(round(rng.uniform(500, 25000), 2)))
        # Mostly modest moves, with the occasional big winner or loser.
        profit_loss = Decimal(str(round(rng.choice([rng.uniform(-15, 30), rng.uniform(-15, 30), rng.uniform(30, 90)]), 2)))
        value = (invested * (Decimal("1") + profit_loss / Decimal("100"))).quantize(Decimal("0.01"))
        positions.append({
            "market": symbol,
            "name": name,
            "logo_url": FMP_LOGO_URL.format(symbol=symbol),
            "direction": "SHORT" if rng.random() < 0.1 else "LONG",
            "invested": invested,
            "profit_loss": profit_loss,
            "value": value,
        })
    return positions
