# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='cryptokey',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='domain',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='domainmetadata',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='record',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='supermaster',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='tsigkey',
            options={'managed': False},
        ),
    ]
