# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calltoaction', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='calltoactionrepository',
            options={'verbose_name': 'Call to Action', 'verbose_name_plural': 'Call to Action Repository'},
        ),
        migrations.AlterModelOptions(
            name='calltoactionrepositorytranslation',
            options={'default_permissions': (), 'verbose_name': 'Call to Action Translation', 'managed': True},
        ),
        migrations.AlterField(
            model_name='calltoactionrepository',
            name='style',
            field=models.CharField(default=b'calltoaction/default.html', max_length=200, choices=[(b'calltoaction/default.html', b'Default'), (b'calltoaction/newsletter.html', b'Newsletter Signup'), (b'calltoaction/popup-form.html', b'Popup form')]),
            preserve_default=True,
        ),
    ]
