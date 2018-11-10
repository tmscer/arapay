# Generated by Django 2.1.2 on 2018-11-10 00:46

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_invoice_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='groups',
            field=models.ManyToManyField(null=True, to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='users',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
