# Generated by Django 2.1.2 on 2018-10-24 07:18

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_auto_20181020_1633'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_number', models.PositiveIntegerField(validators=[django.core.validators.RegexValidator('^\\d{4,10}$')], verbose_name='account number')),
                ('bank_code', models.CharField(max_length=4, validators=[django.core.validators.RegexValidator('^\\d{4}$')], verbose_name='bank code')),
            ],
        ),
        migrations.AddField(
            model_name='invoice',
            name='account_info',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.AccountInfo'),
        ),
    ]
