# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.CharField(blank=True, default='👤', help_text='Avatar emoji or short identifier', max_length=10),
        ),
    ]

