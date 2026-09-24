from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import Trader, TraderPortfolio
from app.portfolio_generator import generate_positions


class Command(BaseCommand):
    help = "Generate random portfolio positions (placeholder data) for traders that have none."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete and regenerate positions for ALL traders, not just those without any.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        traders = Trader.objects.all()
        if not options["force"]:
            traders = traders.exclude(id__in=TraderPortfolio.objects.values("trader_id"))
        else:
            TraderPortfolio.objects.filter(trader__in=traders).delete()

        count = 0
        for trader in traders:
            TraderPortfolio.objects.bulk_create(
                [TraderPortfolio(trader=trader, **p) for p in generate_positions()]
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Generated portfolios for {count} trader(s)."))
