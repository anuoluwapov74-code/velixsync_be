from django.core.management.base import BaseCommand
from app.models import AdminWallet
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed AdminWallet entries with test data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing admin wallets before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted_count = AdminWallet.objects.all().delete()[0]
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing admin wallets')
            )

        wallets_data = [
            {
                "currency": "BTC",
                "amount": Decimal("97250.000000"),
                "wallet_address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "is_active": True,
            },
            {
                "currency": "ETH",
                "amount": Decimal("3450.500000"),
                "wallet_address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                "is_active": True,
            },
            {
                "currency": "SOL",
                "amount": Decimal("198.750000"),
                "wallet_address": "7EcDhSYGxXyscszYEp35KHN8vvw3svAuLKTzXwCFLtV",
                "is_active": True,
            },
            {
                "currency": "USDT ERC20",
                "amount": Decimal("1.000000"),
                "wallet_address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "is_active": True,
            },
            {
                "currency": "USDT TRC20",
                "amount": Decimal("1.000000"),
                "wallet_address": "TN3W4H6rK2ce4vX9YnFQHwKENnHjoxb3m9",
                "is_active": True,
            },
            {
                "currency": "BNB",
                "amount": Decimal("645.300000"),
                "wallet_address": "bnb1grpf0955h0ykzq3ar5nmum7y6gdfl6lxfn46h2",
                "is_active": True,
            },
            {
                "currency": "TRX",
                "amount": Decimal("0.245000"),
                "wallet_address": "TJCnKsPa7y5okkXvQAidZBzqx3QyQ6sxMW",
                "is_active": True,
            },
            {
                "currency": "USDC",
                "amount": Decimal("1.000000"),
                "wallet_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                "is_active": True,
            },
            {
                "currency": "XRP",
                "amount": Decimal("2.350000"),
                "wallet_address": "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
                "is_active": True,
            },
        ]

        created = 0
        updated = 0
        for data in wallets_data:
            wallet, was_created = AdminWallet.objects.update_or_create(
                currency=data["currency"],
                defaults={
                    "amount": data["amount"],
                    "wallet_address": data["wallet_address"],
                    "is_active": data["is_active"],
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Done! Created {created} wallets, updated {updated} wallets. '
                f'Total: {AdminWallet.objects.count()} admin wallets.'
            )
        )
