# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0004_auto_20151218_0741'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budgetestimate',
            name='repeat',
        ),
    ]
