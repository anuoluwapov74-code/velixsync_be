from django.db import migrations


def generate_for_existing_traders(apps, schema_editor):
    """Give every trader that has no portfolio positions a randomly generated one (placeholder data)."""
    from app.portfolio_generator import generate_positions

    Trader = apps.get_model("app", "Trader")
    TraderPortfolio = apps.get_model("app", "TraderPortfolio")

    with_positions = set(TraderPortfolio.objects.values_list("trader_id", flat=True))
    rows = []
    for trader in Trader.objects.exclude(id__in=with_positions):
        rows.extend(TraderPortfolio(trader=trader, **p) for p in generate_positions())
    TraderPortfolio.objects.bulk_create(rows)


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0027_traderportfolio_name_logo"),
    ]

    operations = [
        migrations.RunPython(generate_for_existing_traders, migrations.RunPython.noop),
    ]
