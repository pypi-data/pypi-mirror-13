# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calltoaction', '0002_auto_20150731_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calltoactionrepository',
            name='style',
            field=models.CharField(default=b'calltoaction/default.html', max_length=200, choices=[(b'calltoaction/default.html', b'Default'), (b'calltoaction/newsletter.html', b'Newsletter Signup'), (b'calltoaction/popup-form.html', b'Popup form'), (b'calltoaction/freetips.html', b'Free Tips Signup')]),
            preserve_default=True,
        ),
    ]
