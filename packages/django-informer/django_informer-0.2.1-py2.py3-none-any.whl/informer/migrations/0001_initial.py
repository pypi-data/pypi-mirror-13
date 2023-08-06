# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Raw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('indicator', models.CharField(max_length=255)),
                ('measure', models.CharField(max_length=255)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('value', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['-date', 'indicator', 'measure'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='raw',
            unique_together=set([('indicator', 'measure', 'date')]),
        ),
        migrations.AlterIndexTogether(
            name='raw',
            index_together=set([('indicator', 'measure', 'date')]),
        ),
    ]
