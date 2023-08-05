# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20150527_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', mezzanine.core.fields.OrderField(null=True, verbose_name='Order')),
                ('content', models.TextField(verbose_name='Content')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('date', models.DateField(null=True, verbose_name='Date of realization', blank=True)),
                ('image', models.ImageField(null=True, upload_to=b'references', blank=True)),
                ('link', models.CharField(max_length=128, null=True, verbose_name='Link', blank=True)),
                ('link_title', models.CharField(max_length=32, null=True, verbose_name='Link title', blank=True)),
                ('link_new_window', models.BooleanField(default=False, verbose_name='Open link on new page')),
            ],
            options={
                'ordering': ('_order',),
            },
        ),
        migrations.CreateModel(
            name='References',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pages.Page')),
                ('image_style', models.CharField(default=b'default', max_length=12, verbose_name='Image style', choices=[(b'rounded', 'Rounded'), (b'circle', 'Circle'), (b'thumbnail', 'Thumbnail'), (b'default', 'Default')])),
                ('image_size', models.PositiveIntegerField(default=200, verbose_name='Image width in pixels')),
                ('link_style', models.CharField(default=b'button', max_length=12, verbose_name='Link style', choices=[(b'button', 'Button'), (b'text', 'Text')])),
                ('button_style', models.CharField(default=b'default', max_length=12, verbose_name='Button style', choices=[(b'default', b'default'), (b'primary', b'primary'), (b'info', b'info'), (b'warning', b'warning'), (b'danger', b'danger')])),
            ],
            options={
                'ordering': ('_order',),
            },
            bases=('pages.page',),
        ),
        migrations.AddField(
            model_name='reference',
            name='page',
            field=models.ForeignKey(to='mezzanine_references.References'),
        ),
    ]
