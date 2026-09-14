from django.core.management.base import BaseCommand
from app.models import Signal
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed 6 trading signals for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing signals before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted_count = Signal.objects.all().delete()[0]
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing signals')
            )

        now = timezone.now()

        signals_data = [
            {
                "name": "AAPL",
                "signal_type": "stock",
                "price": Decimal("49.99"),
                "signal_strength": Decimal("94.50"),
                "market_analysis": "Apple shows strong bullish momentum following record iPhone sales and services revenue growth. Technical indicators confirm upward trend with RSI at 62 and MACD showing positive divergence.",
                "entry_point": "$185.00 - $187.50",
                "target_price": "$210.00",
                "stop_loss": "$178.00",
                "action": "BUY",
                "timeframe": "1-2 weeks",
                "risk_level": "low",
                "technical_indicators": "RSI: 62, MACD: Bullish crossover, 50-day MA support, Volume surge above average",
                "fundamental_analysis": "Strong Q4 earnings beat, services revenue at all-time high, robust demand for iPhone 16 Pro",
                "status": "active",
                "is_featured": True,
                "is_active": True,
                "expires_at": now + timedelta(days=14),
            },
            {
                "name": "BTC/USD",
                "signal_type": "crypto",
                "price": Decimal("79.99"),
                "signal_strength": Decimal("97.20"),
                "market_analysis": "Bitcoin approaching key resistance level at $105K with strong institutional inflows. ETF volumes hitting record highs. On-chain metrics show accumulation phase by long-term holders.",
                "entry_point": "$97,000 - $98,500",
                "target_price": "$115,000",
                "stop_loss": "$92,000",
                "action": "BUY",
                "timeframe": "2-4 weeks",
                "risk_level": "medium",
                "technical_indicators": "RSI: 58, Bollinger Bands tightening, Hash rate at ATH, 200-day MA support",
                "fundamental_analysis": "Spot ETF inflows exceeding $500M daily, halving supply shock, institutional adoption accelerating",
                "status": "active",
                "is_featured": True,
                "is_active": True,
                "expires_at": now + timedelta(days=28),
            },
            {
                "name": "EUR/USD",
                "signal_type": "forex",
                "price": Decimal("34.99"),
                "signal_strength": Decimal("82.30"),
                "market_analysis": "EUR/USD showing signs of reversal at support. ECB rate decision upcoming with hawkish expectations. Dollar weakness expected on soft jobs data.",
                "entry_point": "1.0820 - 1.0850",
                "target_price": "1.1050",
                "stop_loss": "1.0750",
                "action": "BUY",
                "timeframe": "1-3 days",
                "risk_level": "medium",
                "technical_indicators": "RSI: 38 (oversold), Stochastic crossover, Fibonacci 61.8% retracement support",
                "fundamental_analysis": "ECB expected to hold rates, US NFP likely to miss consensus, diverging monetary policy outlook",
                "status": "active",
                "is_featured": False,
                "is_active": True,
                "expires_at": now + timedelta(days=3),
            },
            {
                "name": "NVDA",
                "signal_type": "stock",
                "price": Decimal("59.99"),
                "signal_strength": Decimal("91.80"),
                "market_analysis": "NVIDIA continues to benefit from AI infrastructure spending boom. Data center revenue expected to surpass estimates. New Blackwell architecture driving enterprise adoption.",
                "entry_point": "$490.00 - $500.00",
                "target_price": "$580.00",
                "stop_loss": "$465.00",
                "action": "BUY",
                "timeframe": "2-3 weeks",
                "risk_level": "medium",
                "technical_indicators": "RSI: 55, Cup and handle pattern forming, Strong volume profile, Above all major MAs",
                "fundamental_analysis": "AI capex cycle accelerating, Blackwell production ramping, data center TAM expanding to $400B+",
                "status": "active",
                "is_featured": True,
                "is_active": True,
                "expires_at": now + timedelta(days=21),
            },
            {
                "name": "XAU/USD",
                "signal_type": "commodity",
                "price": Decimal("44.99"),
                "signal_strength": Decimal("88.60"),
                "market_analysis": "Gold consolidating near all-time highs with central bank buying remaining robust. Geopolitical tensions and de-dollarization narrative supporting prices. Seasonal demand pickup expected.",
                "entry_point": "$2,380 - $2,400",
                "target_price": "$2,550",
                "stop_loss": "$2,320",
                "action": "BUY",
                "timeframe": "1-2 weeks",
                "risk_level": "low",
                "technical_indicators": "RSI: 51, Bull flag pattern, Strong 20-day MA support, MACD above signal line",
                "fundamental_analysis": "Central bank gold purchases at record pace, real yields declining, safe-haven demand elevated",
                "status": "active",
                "is_featured": False,
                "is_active": True,
                "expires_at": now + timedelta(days=14),
            },
            {
                "name": "ETH/USD",
                "signal_type": "crypto",
                "price": Decimal("54.99"),
                "signal_strength": Decimal("85.40"),
                "market_analysis": "Ethereum showing relative strength with upcoming network upgrades. Staking yields remain attractive. Layer 2 ecosystem growth driving demand for ETH as gas token.",
                "entry_point": "$3,400 - $3,500",
                "target_price": "$4,200",
                "stop_loss": "$3,150",
                "action": "BUY",
                "timeframe": "2-4 weeks",
                "risk_level": "high",
                "technical_indicators": "RSI: 48, Ascending triangle breakout imminent, Volume increasing on green candles",
                "fundamental_analysis": "ETH ETF flows positive, staking APY at 4.2%, L2 TVL growing 15% MoM, deflationary supply",
                "status": "active",
                "is_featured": True,
                "is_active": True,
                "expires_at": now + timedelta(days=28),
            },
        ]

        created_count = 0
        updated_count = 0

        for signal_data in signals_data:
            signal, created = Signal.objects.update_or_create(
                name=signal_data["name"],
                signal_type=signal_data["signal_type"],
                defaults=signal_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created signal: {signal.name} ({signal.signal_type}) - ${signal.price}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⟳ Updated signal: {signal.name} ({signal.signal_type}) - ${signal.price}')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS(f'Signals created: {created_count}'))
        self.stdout.write(self.style.WARNING(f'Signals updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total signals in database: {Signal.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
