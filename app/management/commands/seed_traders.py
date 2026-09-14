from django.core.management.base import BaseCommand
from app.models import Trader
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed 5 professional traders for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing traders before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted_count = Trader.objects.all().delete()[0]
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing traders')
            )

        traders_data = [
            {
                "name": "Kristijan Novak",
                "username": "@kristijan",
                "country": "Germany",
                "badge": "gold",
                "gain": Decimal("126799.00"),
                "risk": 4,
                "capital": "250000",
                "copiers": 287,
                "avg_trade_time": "2 weeks",
                "trades": 1326,
                "subscribers": 194,
                "current_positions": 8,
                "min_account_threshold": Decimal("50000.00"),
                "expert_rating": Decimal("4.90"),
                "return_ytd": Decimal("2187.00"),
                "return_2y": Decimal("8450.00"),
                "avg_score_7d": Decimal("9.30"),
                "profitable_weeks": Decimal("92.00"),
                "total_trades_12m": 485,
                "avg_profit_percent": Decimal("86.00"),
                "avg_loss_percent": Decimal("8.00"),
                "total_wins": 1166,
                "total_losses": 160,
                "performance_data": [
                    {"month": "Jan", "value": 12.5},
                    {"month": "Feb", "value": 8.3},
                    {"month": "Mar", "value": 15.1},
                    {"month": "Apr", "value": -2.4},
                    {"month": "May", "value": 18.7},
                    {"month": "Jun", "value": 9.8},
                ],
                "frequently_traded": ["BTC/USD", "ETH/USD", "AAPL", "TSLA"],
                "is_active": True,
                # New fields
                "bio": "Professional trader with 10+ years of experience in crypto and equity markets. Focused on long-term value with calculated risk management.",
                "followers": 8704,
                "trading_days": "500+",
                "trend_direction": "upward",
                "tags": ["Trending Investors", "Rising Stars"],
                "category": "crypto",
                "max_drawdown": Decimal("12.50"),
                "cumulative_earnings_copiers": Decimal("4520000.00"),
                "cumulative_copiers": 1071,
                "portfolio_breakdown": [
                    {"name": "Crypto", "percentage": 45},
                    {"name": "Stocks", "percentage": 30},
                    {"name": "ETF", "percentage": 25},
                ],
                "top_traded": [
                    {"name": "Bitcoin", "ticker": "BTC/USD", "avg_profit": 18.5, "avg_loss": -4.2, "profitable_pct": 82},
                    {"name": "Ethereum", "ticker": "ETH/USD", "avg_profit": 14.3, "avg_loss": -5.8, "profitable_pct": 76},
                    {"name": "Apple Inc", "ticker": "AAPL", "avg_profit": 8.7, "avg_loss": -2.1, "profitable_pct": 88},
                    {"name": "Tesla Inc", "ticker": "TSLA", "avg_profit": 22.1, "avg_loss": -9.4, "profitable_pct": 71},
                ],
            },
            {
                "name": "Sarah Chen",
                "username": "@sarachen",
                "country": "Singapore",
                "badge": "gold",
                "gain": Decimal("84320.50"),
                "risk": 3,
                "capital": "500000",
                "copiers": 215,
                "avg_trade_time": "1 week",
                "trades": 982,
                "subscribers": 158,
                "current_positions": 5,
                "min_account_threshold": Decimal("25000.00"),
                "expert_rating": Decimal("4.80"),
                "return_ytd": Decimal("1540.00"),
                "return_2y": Decimal("5320.00"),
                "avg_score_7d": Decimal("9.10"),
                "profitable_weeks": Decimal("88.50"),
                "total_trades_12m": 362,
                "avg_profit_percent": Decimal("72.00"),
                "avg_loss_percent": Decimal("12.00"),
                "total_wins": 810,
                "total_losses": 172,
                "performance_data": [
                    {"month": "Jan", "value": 9.2},
                    {"month": "Feb", "value": 14.6},
                    {"month": "Mar", "value": 7.8},
                    {"month": "Apr", "value": 11.3},
                    {"month": "May", "value": -1.5},
                    {"month": "Jun", "value": 16.4},
                ],
                "frequently_traded": ["GOOGL", "AMZN", "SOL/USD", "NVDA"],
                "is_active": True,
                "bio": "Tech-focused investor specializing in AI and semiconductor stocks. Data-driven approach with consistent returns.",
                "followers": 5230,
                "trading_days": "380+",
                "trend_direction": "upward",
                "tags": ["Tech Expert", "Consistent Returns"],
                "category": "tech",
                "max_drawdown": Decimal("8.20"),
                "cumulative_earnings_copiers": Decimal("2870000.00"),
                "cumulative_copiers": 645,
                "portfolio_breakdown": [
                    {"name": "Stocks", "percentage": 55},
                    {"name": "Crypto", "percentage": 25},
                    {"name": "ETF", "percentage": 20},
                ],
                "top_traded": [
                    {"name": "Alphabet Inc", "ticker": "GOOGL", "avg_profit": 12.8, "avg_loss": -3.5, "profitable_pct": 85},
                    {"name": "Amazon", "ticker": "AMZN", "avg_profit": 10.2, "avg_loss": -4.1, "profitable_pct": 80},
                    {"name": "NVIDIA", "ticker": "NVDA", "avg_profit": 25.6, "avg_loss": -7.3, "profitable_pct": 78},
                    {"name": "Solana", "ticker": "SOL/USD", "avg_profit": 16.4, "avg_loss": -8.9, "profitable_pct": 68},
                ],
            },
            {
                "name": "Marcus Williams",
                "username": "@marcusw",
                "country": "United States",
                "badge": "silver",
                "gain": Decimal("45210.75"),
                "risk": 6,
                "capital": "100000",
                "copiers": 143,
                "avg_trade_time": "3 days",
                "trades": 2150,
                "subscribers": 89,
                "current_positions": 12,
                "min_account_threshold": Decimal("10000.00"),
                "expert_rating": Decimal("4.60"),
                "return_ytd": Decimal("890.00"),
                "return_2y": Decimal("3120.00"),
                "avg_score_7d": Decimal("8.50"),
                "profitable_weeks": Decimal("78.00"),
                "total_trades_12m": 720,
                "avg_profit_percent": Decimal("55.00"),
                "avg_loss_percent": Decimal("15.00"),
                "total_wins": 1580,
                "total_losses": 570,
                "performance_data": [
                    {"month": "Jan", "value": 5.4},
                    {"month": "Feb", "value": -3.2},
                    {"month": "Mar", "value": 22.1},
                    {"month": "Apr", "value": 8.9},
                    {"month": "May", "value": 12.6},
                    {"month": "Jun", "value": -1.8},
                ],
                "frequently_traded": ["EUR/USD", "GBP/USD", "XAU/USD", "BTC/USD"],
                "is_active": True,
                "bio": "High-frequency trader with aggressive strategies. Specializing in forex and gold trading with quick turnarounds.",
                "followers": 3120,
                "trading_days": "720+",
                "trend_direction": "upward",
                "tags": ["Active Trader", "Forex Specialist"],
                "category": "options",
                "max_drawdown": Decimal("22.30"),
                "cumulative_earnings_copiers": Decimal("1450000.00"),
                "cumulative_copiers": 389,
                "portfolio_breakdown": [
                    {"name": "Futures", "percentage": 50},
                    {"name": "Crypto", "percentage": 25},
                    {"name": "ETF", "percentage": 25},
                ],
                "top_traded": [
                    {"name": "Euro/Dollar", "ticker": "EUR/USD", "avg_profit": 6.2, "avg_loss": -3.8, "profitable_pct": 72},
                    {"name": "Gold", "ticker": "XAU/USD", "avg_profit": 9.5, "avg_loss": -5.1, "profitable_pct": 68},
                    {"name": "Bitcoin", "ticker": "BTC/USD", "avg_profit": 15.8, "avg_loss": -8.2, "profitable_pct": 65},
                ],
            },
            {
                "name": "Elena Petrova",
                "username": "@elenap",
                "country": "Switzerland",
                "badge": "gold",
                "gain": Decimal("97450.30"),
                "risk": 2,
                "capital": "1000000",
                "copiers": 312,
                "avg_trade_time": "1 month",
                "trades": 654,
                "subscribers": 245,
                "current_positions": 3,
                "min_account_threshold": Decimal("75000.00"),
                "expert_rating": Decimal("5.00"),
                "return_ytd": Decimal("1820.00"),
                "return_2y": Decimal("6780.00"),
                "avg_score_7d": Decimal("9.70"),
                "profitable_weeks": Decimal("95.00"),
                "total_trades_12m": 198,
                "avg_profit_percent": Decimal("90.00"),
                "avg_loss_percent": Decimal("5.00"),
                "total_wins": 612,
                "total_losses": 42,
                "performance_data": [
                    {"month": "Jan", "value": 18.2},
                    {"month": "Feb", "value": 12.4},
                    {"month": "Mar", "value": 9.7},
                    {"month": "Apr", "value": 14.1},
                    {"month": "May", "value": 8.9},
                    {"month": "Jun", "value": 20.3},
                ],
                "frequently_traded": ["AAPL", "MSFT", "NVDA", "META"],
                "is_active": True,
                "bio": "Conservative wealth manager with institutional-grade strategies. Low risk, high consistency. Former Goldman Sachs portfolio manager.",
                "followers": 12400,
                "trading_days": "1200+",
                "trend_direction": "upward",
                "tags": ["Top Performer", "Low Risk", "Institutional"],
                "category": "stocks",
                "max_drawdown": Decimal("4.80"),
                "cumulative_earnings_copiers": Decimal("8920000.00"),
                "cumulative_copiers": 2340,
                "portfolio_breakdown": [
                    {"name": "Stocks", "percentage": 40},
                    {"name": "ETF", "percentage": 35},
                    {"name": "Crypto", "percentage": 15},
                    {"name": "Futures", "percentage": 10},
                ],
                "top_traded": [
                    {"name": "Apple Inc", "ticker": "AAPL", "avg_profit": 11.2, "avg_loss": -1.8, "profitable_pct": 94},
                    {"name": "Microsoft", "ticker": "MSFT", "avg_profit": 9.8, "avg_loss": -2.3, "profitable_pct": 91},
                    {"name": "NVIDIA", "ticker": "NVDA", "avg_profit": 18.5, "avg_loss": -3.6, "profitable_pct": 89},
                    {"name": "Meta Platforms", "ticker": "META", "avg_profit": 13.4, "avg_loss": -2.9, "profitable_pct": 87},
                ],
            },
            {
                "name": "Takeshi Yamamoto",
                "username": "@takeshi",
                "country": "Japan",
                "badge": "silver",
                "gain": Decimal("32180.60"),
                "risk": 7,
                "capital": "75000",
                "copiers": 98,
                "avg_trade_time": "1 day",
                "trades": 3420,
                "subscribers": 67,
                "current_positions": 15,
                "min_account_threshold": Decimal("5000.00"),
                "expert_rating": Decimal("4.50"),
                "return_ytd": Decimal("620.00"),
                "return_2y": Decimal("2450.00"),
                "avg_score_7d": Decimal("7.80"),
                "profitable_weeks": Decimal("72.00"),
                "total_trades_12m": 1280,
                "avg_profit_percent": Decimal("48.00"),
                "avg_loss_percent": Decimal("20.00"),
                "total_wins": 2394,
                "total_losses": 1026,
                "performance_data": [
                    {"month": "Jan", "value": -4.1},
                    {"month": "Feb", "value": 28.5},
                    {"month": "Mar", "value": 6.3},
                    {"month": "Apr", "value": -7.2},
                    {"month": "May", "value": 35.8},
                    {"month": "Jun", "value": 11.4},
                ],
                "frequently_traded": ["BTC/USD", "ETH/USD", "SOL/USD", "DOGE/USD"],
                "is_active": True,
                "bio": "Day trader and crypto enthusiast. High volume, high risk, high reward. Specializing in volatile markets and momentum plays.",
                "followers": 1890,
                "trading_days": "300+",
                "trend_direction": "downward",
                "tags": ["Day Trader", "High Risk"],
                "category": "crypto",
                "max_drawdown": Decimal("35.60"),
                "cumulative_earnings_copiers": Decimal("890000.00"),
                "cumulative_copiers": 267,
                "portfolio_breakdown": [
                    {"name": "Crypto", "percentage": 70},
                    {"name": "Futures", "percentage": 20},
                    {"name": "Stocks", "percentage": 10},
                ],
                "top_traded": [
                    {"name": "Bitcoin", "ticker": "BTC/USD", "avg_profit": 24.6, "avg_loss": -12.3, "profitable_pct": 62},
                    {"name": "Ethereum", "ticker": "ETH/USD", "avg_profit": 19.8, "avg_loss": -10.5, "profitable_pct": 58},
                    {"name": "Solana", "ticker": "SOL/USD", "avg_profit": 32.4, "avg_loss": -18.7, "profitable_pct": 55},
                    {"name": "Dogecoin", "ticker": "DOGE/USD", "avg_profit": 45.2, "avg_loss": -25.6, "profitable_pct": 48},
                ],
            },
        ]

        created_count = 0
        updated_count = 0

        for trader_data in traders_data:
            trader, created = Trader.objects.update_or_create(
                username=trader_data["username"],
                defaults=trader_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created trader: {trader.name} ({trader.username})')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated trader: {trader.name} ({trader.username})')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS(f'Traders created: {created_count}'))
        self.stdout.write(self.style.WARNING(f'Traders updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total traders in database: {Trader.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
