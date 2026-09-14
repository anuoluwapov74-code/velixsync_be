from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_trader_profit_share'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='source',
            field=models.CharField(
                blank=True,
                choices=[('balance', 'Main Balance'), ('profit', 'Profit')],
                default='balance',
                max_length=10,
            ),
        ),
    ]
