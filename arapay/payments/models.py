from datetime import datetime as dt

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.validators import MaxValueValidator
from django.db import models

User = get_user_model()


class Invoice(models.Model):
    name = models.fields.CharField('invoice name', max_length=32)
    description = models.fields.TextField('payment description', max_length=200, blank=True)
    date_added = models.fields.DateField('date added', default=dt.now)
    date_deadline = models.fields.DateField('date due')
    amount_cents = models.fields.BigIntegerField('amount in cents')
    groups = models.ManyToManyField(Group)

    def __repr__(self):
        return "Invoice(name={}, description={}, date_added={}, date_deadline={}, amount_cents={})" \
            .format(self.name, self.description, self.date_added, self.date_deadline, self.amount_cents)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'invoice'
        verbose_name_plural = 'invoices'


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_cents = models.fields.BigIntegerField('amount in cents', default=0)
    date_paid = models.fields.DateField('date paid', default=dt.now)
    var_symbol = models.fields.PositiveIntegerField('associated var symbol', default=0,
                                                    validators=[MaxValueValidator(9999999999)])

    def __repr__(self):
        return "Payment(invoice={}, user={}, amount_cents={})" \
            .format(self.invoice, self.user, self.amount_cents)

    def __str__(self):
        return "{} {}" \
            .format(self.invoice, self.user)

    class Meta:
        verbose_name = 'payment'
        verbose_name_plural = 'payments'
        unique_together = (("invoice", "user"),)

    class Status:
        PAID = 'paid'
        UNPAID = 'unpaid'
        OVERPAID = 'overpaid'
