from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_customuser_show_portfolio_growth'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='category',
            field=models.CharField(
                choices=[
                    ('stock', 'Stock'),
                    ('crypto', 'Crypto'),
                    ('etf', 'ETF'),
                    ('indices', 'Indices'),
                    ('forex', 'Forex'),
                ],
                default='stock',
                max_length=20,
            ),
        ),
    ]
