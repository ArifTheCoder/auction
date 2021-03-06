# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-28 12:01
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auction_title', models.CharField(max_length=600)),
                ('description', models.CharField(max_length=5000)),
                ('currency', models.CharField(max_length=20)),
                ('token_edit', models.CharField(max_length=600)),
                ('starting_price', models.DecimalField(decimal_places=2, max_digits=19, max_length=30)),
                ('bidding_price', models.DecimalField(decimal_places=2, max_digits=19, max_length=30, null=True)),
                ('winner_id', models.IntegerField(null=True)),
                ('starting_date', models.DateTimeField(blank=True)),
                ('auction_duration_hours', models.IntegerField(default=72, validators=[django.core.validators.MinValueValidator(72)])),
                ('ending_date', models.DateTimeField(blank=True)),
                ('auction_status', models.CharField(choices=[('Active', 'Active'), ('Banned', 'Banned'), ('Due', 'Due'), ('Adjudicated', 'Adjudicated')], default='Active', max_length=20)),
                ('auction_revision', models.IntegerField(default=1)),
                ('seller_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bidding_value', models.DecimalField(decimal_places=2, max_digits=19, max_length=30)),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.Auction')),
                ('bidder_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SetCurrency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=20)),
                ('value', models.DecimalField(decimal_places=4, max_digits=19)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_language', models.CharField(default='en', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
