from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_generate_trader_portfolios'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trader',
            name='blur_portfolio_amount',
        ),
    ]
