# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_page_featured_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaqPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pages.Page')),
            ],
            options={
                'ordering': ('_order',),
                'verbose_name': 'FAQ',
                'verbose_name_plural': 'FAQ',
            },
            bases=('pages.page',),
        ),
        migrations.CreateModel(
            name='FaqQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', mezzanine.core.fields.OrderField(null=True, verbose_name='Order')),
                ('question', models.TextField(verbose_name='Question')),
                ('answer', models.TextField(verbose_name='Answer')),
                ('page', models.ForeignKey(to='mezzanine_faq.FaqPage')),
            ],
            options={
                'ordering': ('_order',),
                'verbose_name': 'Question',
                'verbose_name_plural': 'Questions',
            },
        ),
    ]
