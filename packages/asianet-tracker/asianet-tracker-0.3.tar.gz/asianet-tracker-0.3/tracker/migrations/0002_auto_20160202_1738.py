from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tracker',
            name='path',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='tracker',
            name='user_agent',
            field=models.TextField(null=True, blank=True),
        ),
    ]
