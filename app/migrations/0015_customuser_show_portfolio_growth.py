from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_customuser_target'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='show_portfolio_growth',
            field=models.BooleanField(default=False, help_text="Show Portfolio Growth Target section on the user's portfolio page"),
        ),
    ]
