# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import trustedhtml.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255, null=True, verbose_name='URL', blank=True)),
                ('block_id', models.CharField(max_length=25, verbose_name='\u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440 \u0431\u043b\u043e\u043a\u0430')),
                ('text', trustedhtml.fields.TrustedHTMLField(verbose_name='\u0442\u0435\u043a\u0441\u0442')),
            ],
            options={
                'verbose_name': '\u0442\u0435\u043a\u0441\u0442\u043e\u0432\u044b\u0439 \u0431\u043b\u043e\u043a',
                'verbose_name_plural': '\u0442\u0435\u043a\u0441\u0442\u043e\u0432\u044b\u0435 \u0431\u043b\u043e\u043a\u0438',
            },
        ),
        migrations.AlterUniqueTogether(
            name='siteblock',
            unique_together=set([('url', 'block_id')]),
        ),
        migrations.AlterIndexTogether(
            name='siteblock',
            index_together=set([('url', 'block_id')]),
        ),
    ]
