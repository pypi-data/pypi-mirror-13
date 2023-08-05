# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0028_newversionblock'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentVersionEXIFData',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'tag', models.CharField(
                        max_length=255, verbose_name='Tag'
                    )
                ),
                (
                    'value', models.CharField(
                        max_length=255, verbose_name='Value'
                    )
                ),
                (
                    'document_version', models.ForeignKey(
                        related_name='exif', verbose_name='Document version',
                        to='documents.DocumentVersion'
                    )
                ),
            ],
            options={
                'verbose_name': 'Document version EXIF data',
                'verbose_name_plural': 'Document versions EXIF data',
            },
            bases=(models.Model,),
        ),
    ]
