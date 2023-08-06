# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='redirect_uri',
            field=models.TextField(help_text=b"Your application's callback URLs in a comma-delimited list."),
        ),
    ]
