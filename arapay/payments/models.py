from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Invoice(models.Model):
    date_added = models.fields.DateTimeField('date added')
    date_deadline = models.fields.DateTimeField('date due')
    payment_group = models.fields.TextField('payment group', max_length=64)
    description = models.fields.TextField('payment description', max_length=200)
    amount_cents = models.fields.BigIntegerField('amount in cents')

    def __repr__(self):
        return "Invoice(date_added={}, date_deadline={}, payment_group={}, description={}, amount_cents={})" \
            .format(self.date_added, self.date_deadline, self.payment_group, self.description, self.amount_cents)


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_cents = models.fields.BigIntegerField('amount in cents')

    def __repr__(self):
        return "Payment(invoice={}, user={}, amount_cents={})" \
            .format(self.invoice, self.user, self.amount_cents)
