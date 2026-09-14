from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_customuser_level_of_education'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trader',
            name='min_account_threshold',
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text='Minimum account balance required to copy this trader',
                max_digits=20,
            ),
        ),
        migrations.AlterField(
            model_name='usertradercopy',
            name='initial_investment_amount',
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text='Amount user initially locked in with',
                max_digits=20,
            ),
        ),
        migrations.AlterField(
            model_name='usertradercopy',
            name='minimum_threshold_at_start',
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Trader's minimum threshold when user started copying (for reference only)",
                max_digits=20,
            ),
        ),
    ]
