# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import assetmanager.storage


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name=b'Updated')),
                ('object_id', models.PositiveIntegerField()),
                ('object_field', models.CharField(max_length=100)),
                ('content_type', models.ForeignKey(related_name='attachments', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name=b'Updated')),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('file', models.FileField(storage=assetmanager.storage.GoogleCloudStorage(), upload_to=b'')),
                ('file_original_name', models.CharField(max_length=255)),
                ('file_content_type', models.CharField(max_length=50, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='attachment',
            name='file',
            field=models.ForeignKey(related_name='attachments', to='assetmanager.File'),
        ),
        migrations.RunSQL('CREATE FULLTEXT INDEX assetmanager_file_name_ftidx ON assetmanager_file(name)'),  # nopep8
        migrations.RunSQL('CREATE FULLTEXT INDEX assetmanager_file_description_ftidx ON assetmanager_file(description)'),  # nopep8
        migrations.RunSQL('CREATE FULLTEXT INDEX assetmanager_file_file_original_name_ftidx ON assetmanager_file(file_original_name)'),  # nopep8
    ]
