# Generated by Django 2.1.1 on 2018-09-09 05:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0008_auto_20180908_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='date_paid',
            field=models.DateField(default=datetime.datetime.now, verbose_name='date paid'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='date_added',
            field=models.DateField(default=datetime.datetime.now, verbose_name='date added'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='date_deadline',
            field=models.DateField(verbose_name='date due'),
        ),
    ]
