# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-18 13:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpriceorder',
            name='over_time',
            field=models.DateField(blank=True, null=True, verbose_name='结束时间'),
        ),
    ]