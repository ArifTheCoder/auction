# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-03 11:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0004_auto_20171003_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='newPrice',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
