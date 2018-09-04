from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Invoice(models.Model):
    date_added = models.fields.DateTimeField('date added')
    date_deadine = models.fields.DateTimeField('date due')
    payment_group = models.fields.TextField('payment group', max_length=64)
    description = models.fields.TextField('payment description', max_length=200)
    amount_cents = models.fields.BigIntegerField('amount in cents')


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.fields.BigIntegerField('amount in cents')
