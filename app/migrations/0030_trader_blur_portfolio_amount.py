from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0029_remove_trader_blur_portfolio_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='trader',
            name='blur_portfolio_amount',
            field=models.DecimalField(
                max_digits=20,
                decimal_places=2,
                default=Decimal('50000.00'),
                help_text="Minimum user balance ($) required to view and mirror this trader's portfolio "
                          "(only applies when 'Blur portfolio' is on)",
            ),
        ),
    ]
