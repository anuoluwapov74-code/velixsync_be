import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_transaction_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercopytraderhistory',
            name='custom_image',
            field=cloudinary.models.CloudinaryField(
                blank=True,
                help_text='Custom image for this trade (shown instead of the default market icon)',
                null=True,
                verbose_name='custom_image',
            ),
        ),
    ]
