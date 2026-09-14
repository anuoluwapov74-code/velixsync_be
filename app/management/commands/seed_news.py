from django.core.management.base import BaseCommand
from app.models import News
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed 6 news articles for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing news before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted_count = News.objects.all().delete()[0]
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing news articles')
            )

        now = timezone.now()

        news_data = [
            {
                "title": "Bitcoin Surpasses $100K Mark as Institutional Demand Soars",
                "summary": "Bitcoin has crossed the $100,000 threshold for the first time, driven by unprecedented institutional inflows into spot ETFs and growing adoption as a treasury reserve asset.",
                "content": "Bitcoin has officially surpassed the $100,000 milestone, marking a historic moment for the cryptocurrency market. The surge is attributed to massive institutional demand, particularly through spot Bitcoin ETFs which have seen cumulative inflows exceeding $50 billion since their January 2024 launch.\n\nMajor financial institutions including BlackRock, Fidelity, and Goldman Sachs have significantly increased their Bitcoin holdings, with BlackRock's iShares Bitcoin Trust (IBIT) becoming the fastest-growing ETF in history.\n\nAnalysts predict that the combination of the recent halving event, which reduced the new supply of Bitcoin by half, and the growing institutional adoption could push prices even higher in the coming months. Several Wall Street firms have revised their year-end price targets upward, with some forecasting Bitcoin could reach $150,000 by year-end.\n\nThe broader cryptocurrency market has also benefited from this rally, with Ethereum, Solana, and other major altcoins posting significant gains.",
                "category": "Cryptocurrency",
                "source": "Bloomberg",
                "author": "Michael Chen",
                "published_at": now - timedelta(hours=2),
                "tags": ["Bitcoin", "Cryptocurrency", "ETF", "Institutional Investment"],
                "is_featured": True,
            },
            {
                "title": "NVIDIA Reports Record Revenue on AI Chip Demand Surge",
                "summary": "NVIDIA's quarterly revenue hit an all-time high of $35.1 billion, surpassing analyst estimates as demand for AI training and inference chips continues to accelerate across enterprise customers.",
                "content": "NVIDIA Corporation reported record-breaking quarterly revenue of $35.1 billion, a 122% increase year-over-year, driven by insatiable demand for its AI accelerator chips. The data center segment alone generated $30.8 billion in revenue.\n\nCEO Jensen Huang highlighted the ramp-up of the new Blackwell architecture, which is seeing demand that 'far exceeds supply.' Major cloud providers including Microsoft Azure, Amazon Web Services, and Google Cloud have placed multi-billion dollar orders for the next-generation chips.\n\nThe company also announced a new partnership with several sovereign wealth funds to build AI infrastructure, expanding its total addressable market beyond traditional tech companies. NVIDIA's gross margins remained exceptionally strong at 73.5%, reflecting the premium pricing power of its market-leading GPU products.\n\nShares rose 8% in after-hours trading following the earnings announcement, pushing NVIDIA's market capitalization above $3.5 trillion.",
                "category": "Technology",
                "source": "Reuters",
                "author": "Sarah Williams",
                "published_at": now - timedelta(hours=6),
                "tags": ["NVIDIA", "AI", "Earnings", "Semiconductors"],
                "is_featured": True,
            },
            {
                "title": "Federal Reserve Signals Potential Rate Cut in March Meeting",
                "summary": "Fed Chair Powell indicated the central bank is 'closely monitoring' economic data and may consider adjusting rates at the upcoming March meeting as inflation continues to moderate.",
                "content": "Federal Reserve Chair Jerome Powell signaled during his latest press conference that the central bank is open to cutting interest rates at the March FOMC meeting, citing continued progress on inflation and emerging signs of labor market softening.\n\nThe Consumer Price Index (CPI) has declined for three consecutive months, now sitting at 2.4%, approaching the Fed's 2% target. Meanwhile, the unemployment rate has ticked up to 4.1%, prompting concerns about potential economic slowdown.\n\n'We are seeing encouraging signs that inflation is moving sustainably toward our target,' Powell stated. 'At the same time, we remain attentive to risks on both sides of our mandate.'\n\nMarkets reacted positively to the dovish commentary, with the S&P 500 gaining 1.8% and the 10-year Treasury yield falling to 3.85%. Fed funds futures are now pricing in a 78% probability of a 25 basis point cut in March.\n\nEconomists note that a rate cut could provide a significant boost to both equity and bond markets, particularly benefiting growth stocks and real estate.",
                "category": "Economy",
                "source": "Financial Times",
                "author": "David Rodriguez",
                "published_at": now - timedelta(hours=12),
                "tags": ["Federal Reserve", "Interest Rates", "Economy", "Inflation"],
                "is_featured": False,
            },
            {
                "title": "Tesla Unveils Next-Gen Autonomous Driving Platform at CES",
                "summary": "Tesla revealed its FSD v13 platform featuring custom AI chips capable of full Level 4 autonomy, with plans to launch a robotaxi service in select US cities by Q3.",
                "content": "Tesla has unveiled its next-generation Full Self-Driving (FSD) platform at CES, featuring a completely redesigned neural network architecture running on custom-designed AI chips. The FSD v13 system achieves Level 4 autonomy, meaning it can handle all driving tasks without human intervention in designated areas.\n\nCEO Elon Musk announced that Tesla plans to launch its long-awaited robotaxi service, branded as 'Tesla Rides,' in Austin, San Francisco, and Los Angeles by the third quarter. The service will initially operate with safety drivers before transitioning to fully driverless operations.\n\nThe new platform processes data from 12 cameras, 3 radar units, and 6 LiDAR sensors — marking Tesla's first integration of LiDAR technology. The custom AI chip delivers 500 TOPS (trillion operations per second), a 5x improvement over the previous generation.\n\nTesla shares surged 12% following the announcement, with analysts at Morgan Stanley raising their price target to $350, citing the potential $1 trillion revenue opportunity in autonomous mobility.",
                "category": "Technology",
                "source": "TechCrunch",
                "author": "Amanda Foster",
                "published_at": now - timedelta(days=1),
                "tags": ["Tesla", "Autonomous Driving", "AI", "Electric Vehicles"],
                "is_featured": True,
            },
            {
                "title": "Gold Prices Hit All-Time High Amid Global Uncertainty",
                "summary": "Gold surged past $2,500 per ounce, setting a new record as investors flock to safe-haven assets amid geopolitical tensions and expectations of monetary policy easing.",
                "content": "Gold prices have reached an unprecedented $2,520 per ounce, driven by a confluence of factors including escalating geopolitical tensions, central bank purchasing, and expectations of interest rate cuts by major central banks.\n\nThe World Gold Council reported that central bank gold purchases reached 290 tonnes in Q4, with China, India, and Turkey leading the buying spree. This marks the eighth consecutive quarter of above-average central bank gold acquisitions.\n\n'Gold is benefiting from a perfect storm of bullish factors,' said Mark Thompson, chief strategist at UBS Wealth Management. 'The combination of geopolitical risk, de-dollarization trends, and an approaching rate cut cycle is creating unprecedented demand.'\n\nPhysical gold demand in Asia has also surged, with premiums in Shanghai and Mumbai reaching multi-year highs. Gold-backed ETFs saw inflows of $4.2 billion in January alone, reversing the outflow trend of the previous year.\n\nAnalysts at Goldman Sachs have raised their 12-month gold price forecast to $2,800, citing structural demand from central banks and retail investors.",
                "category": "Commodities",
                "source": "CNBC",
                "author": "James Morrison",
                "published_at": now - timedelta(days=1, hours=8),
                "tags": ["Gold", "Commodities", "Safe Haven", "Central Banks"],
                "is_featured": False,
            },
            {
                "title": "S&P 500 Reaches New Heights as Tech Earnings Exceed Expectations",
                "summary": "The S&P 500 closed at a record 5,850 points after a strong earnings season led by mega-cap technology companies, with the index gaining 4.2% in January alone.",
                "content": "The S&P 500 index has reached a new all-time high of 5,850 points, capping off a remarkable January rally fueled by better-than-expected earnings from the technology sector. The index has gained 4.2% year-to-date, with the Nasdaq Composite outperforming at 5.8%.\n\nThe 'Magnificent Seven' tech stocks — Apple, Microsoft, Amazon, Alphabet, Meta, NVIDIA, and Tesla — collectively reported revenue growth of 18% year-over-year, with earnings per share beating consensus estimates by an average of 12%.\n\nMicrosoft's cloud revenue growth accelerated to 32%, driven by Azure AI services. Meta reported a 28% increase in advertising revenue, attributing the growth to its AI-powered ad targeting algorithms. Amazon's AWS segment posted record operating margins of 37%.\n\nMarket breadth has also improved, with 78% of S&P 500 components trading above their 200-day moving averages. Small-cap stocks, represented by the Russell 2000, gained 3.1%, suggesting the rally is broadening beyond mega-cap tech.\n\nDespite the optimism, some strategists caution that valuations are stretched, with the S&P 500 trading at 22x forward earnings, above its 10-year average of 18x.",
                "category": "Stocks",
                "source": "Wall Street Journal",
                "author": "Patricia Liu",
                "published_at": now - timedelta(days=2),
                "tags": ["S&P 500", "Stocks", "Earnings", "Technology"],
                "is_featured": False,
            },
        ]

        created_count = 0
        updated_count = 0

        for article_data in news_data:
            article, created = News.objects.update_or_create(
                title=article_data["title"],
                defaults=article_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created article: {article.title[:50]}...')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⟳ Updated article: {article.title[:50]}...')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS(f'Articles created: {created_count}'))
        self.stdout.write(self.style.WARNING(f'Articles updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total articles in database: {News.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
