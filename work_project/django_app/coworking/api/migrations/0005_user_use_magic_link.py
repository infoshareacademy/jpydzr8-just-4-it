# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='use_magic_link',
            field=models.BooleanField(default=False, help_text='Use magic link authentication instead of password'),
        ),
    ]

