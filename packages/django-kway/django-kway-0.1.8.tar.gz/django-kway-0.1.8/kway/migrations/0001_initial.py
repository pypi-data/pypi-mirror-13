# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=100, verbose_name=b'Key')),
                ('value', sorl.thumbnail.fields.ImageField(default=b'', upload_to=b'uploads/kway/images/', verbose_name=b'Value', blank=True)),
            ],
            options={
                'ordering': ['key'],
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
            },
        ),
        migrations.CreateModel(
            name='KText',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=100, verbose_name=b'Key')),
                ('value', models.TextField(default=b'', verbose_name=b'Value', blank=True)),
            ],
            options={
                'ordering': ['key'],
                'verbose_name': 'Text',
                'verbose_name_plural': 'Texts',
            },
        ),
    ]
