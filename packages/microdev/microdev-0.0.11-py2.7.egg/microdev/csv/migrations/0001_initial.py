# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CsvImport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('_column_headers', models.TextField(null=True, db_column=b'column_headers')),
                ('notes', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CsvImportRow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_json_data', models.TextField(db_column=b'json_data')),
                ('csv_import', models.ForeignKey(to='csv.CsvImport')),
            ],
        ),
    ]
