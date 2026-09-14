from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_stock_image_alter_customuser_account_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='target',
            field=models.DecimalField(
                decimal_places=2,
                default=50000.0,
                help_text='Admin-set deposit target amount for the portfolio growth bar.',
                max_digits=20,
                verbose_name='Portfolio Target',
            ),
        ),
    ]
