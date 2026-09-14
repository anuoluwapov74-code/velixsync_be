from django.core.management.base import BaseCommand
from app.models import Stock
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create test stock data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing stocks before creating new ones',
        )

    def handle(self, *args, **options):
        # Clear existing stocks if --clear flag is provided
        if options['clear']:
            deleted_count = Stock.objects.all().delete()[0]
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing stocks')
            )

        # Create featured stocks
        stocks_data = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": Decimal("185.50"),
                "change": Decimal("2.35"),
                "change_percent": Decimal("1.28"),
                "volume": 52000000,
                "market_cap": 2850000000000,
                "sector": "Technology",
                "is_featured": True,
                "is_active": True,
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "price": Decimal("395.75"),
                "change": Decimal("5.20"),
                "change_percent": Decimal("1.33"),
                "volume": 28000000,
                "market_cap": 2940000000000,
                "sector": "Technology",
                "is_featured": True,
                "is_active": True,
            },
            {
                "symbol": "GOOGL",
                "name": "Alphabet Inc. Class A",
                "price": Decimal("142.30"),
                "change": Decimal("1.85"),
                "change_percent": Decimal("1.32"),
                "volume": 35000000,
                "market_cap": 1780000000000,
                "sector": "Technology",
                "is_featured": True,
                "is_active": True,
            },
            {
                "symbol": "AMZN",
                "name": "Amazon.com Inc.",
                "price": Decimal("168.25"),
                "change": Decimal("-1.20"),
                "change_percent": Decimal("-0.71"),
                "volume": 48000000,
                "market_cap": 1740000000000,
                "sector": "Consumer Cyclical",
                "is_featured": True,
                "is_active": True,
            },
            {
                "symbol": "TSLA",
                "name": "Tesla Inc.",
                "price": Decimal("245.80"),
                "change": Decimal("-3.50"),
                "change_percent": Decimal("-1.40"),
                "volume": 95000000,
                "market_cap": 780000000000,
                "sector": "Consumer Cyclical",
                "is_featured": True,
                "is_active": True,
            },
            {
                "symbol": "NVDA",
                "name": "NVIDIA Corporation",
                "price": Decimal("495.20"),
                "change": Decimal("12.40"),
                "change_percent": Decimal("2.57"),
                "volume": 42000000,
                "market_cap": 1220000000000,
                "sector": "Technology",
                "is_featured": True,
                "is_active": True,
            },
        ]

        # Non-featured stocks
        other_stocks = [
            {
                "symbol": "META",
                "name": "Meta Platforms Inc.",
                "price": Decimal("385.60"),
                "change": Decimal("4.25"),
                "change_percent": Decimal("1.11"),
                "volume": 18000000,
                "market_cap": 980000000000,
                "sector": "Technology",
                "is_featured": False,
                "is_active": True,
            },
            {
                "symbol": "NFLX",
                "name": "Netflix Inc.",
                "price": Decimal("525.30"),
                "change": Decimal("8.10"),
                "change_percent": Decimal("1.57"),
                "volume": 5500000,
                "market_cap": 230000000000,
                "sector": "Communication Services",
                "is_featured": False,
                "is_active": True,
            },
            {
                "symbol": "JPM",
                "name": "JPMorgan Chase & Co.",
                "price": Decimal("162.45"),
                "change": Decimal("-0.85"),
                "change_percent": Decimal("-0.52"),
                "volume": 12000000,
                "market_cap": 470000000000,
                "sector": "Financial Services",
                "is_featured": False,
                "is_active": True,
            },
            {
                "symbol": "V",
                "name": "Visa Inc. Class A",
                "price": Decimal("265.90"),
                "change": Decimal("2.10"),
                "change_percent": Decimal("0.80"),
                "volume": 7500000,
                "market_cap": 540000000000,
                "sector": "Financial Services",
                "is_featured": False,
                "is_active": True,
            },
            {
                "symbol": "WMT",
                "name": "Walmart Inc.",
                "price": Decimal("168.75"),
                "change": Decimal("1.25"),
                "change_percent": Decimal("0.75"),
                "volume": 8200000,
                "market_cap": 455000000000,
                "sector": "Consumer Defensive",
                "is_featured": False,
                "is_active": True,
            },
            {
                "symbol": "DIS",
                "name": "The Walt Disney Company",
                "price": Decimal("93.80"),
                "change": Decimal("-1.15"),
                "change_percent": Decimal("-1.21"),
                "volume": 11000000,
                "market_cap": 172000000000,
                "sector": "Communication Services",
                "is_featured": False,
                "is_active": True,
            },
        ]

        # Combine all stocks
        all_stocks = stocks_data + other_stocks

        # Create stocks
        created_count = 0
        updated_count = 0

        for stock_data in all_stocks:
            stock, created = Stock.objects.get_or_create(
                symbol=stock_data["symbol"],
                defaults=stock_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created stock: {stock.symbol} - {stock.name}')
                )
            else:
                # Update existing stock with new data
                for key, value in stock_data.items():
                    setattr(stock, key, value)
                stock.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⟳ Updated stock: {stock.symbol} - {stock.name}')
                )

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS(f'Stocks created: {created_count}'))
        self.stdout.write(self.style.WARNING(f'Stocks updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total stocks in database: {Stock.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
