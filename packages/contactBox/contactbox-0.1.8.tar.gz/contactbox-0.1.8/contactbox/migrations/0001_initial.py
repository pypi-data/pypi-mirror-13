# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(help_text=b'Creation date', auto_now_add=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'Name')),
                ('email', models.EmailField(max_length=254, verbose_name=b'Email address')),
                ('organization', models.CharField(max_length=255, verbose_name=b'Organization', blank=True)),
                ('phone', models.CharField(max_length=20, verbose_name=b'Phone', blank=True)),
                ('message', models.TextField(verbose_name=b'Comments')),
                ('notification_date', models.DateTimeField(help_text=b'When notification was send', null=True, editable=False, blank=True)),
                ('unread', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Receiver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
