from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models

User = get_user_model()


class Invoice(models.Model):
    name = models.fields.CharField('invoice name', max_length=32)
    description = models.fields.TextField('payment description', max_length=200)
    date_added = models.fields.DateTimeField('date added')
    date_deadline = models.fields.DateTimeField('date due')
    amount_cents = models.fields.BigIntegerField('amount in cents')
    groups = models.ManyToManyField(Group)

    def __repr__(self):
        return "Invoice(name={}, description={}, date_added={}, date_deadline={}, amount_cents={})" \
            .format(self.name, self.description, self.date_added, self.date_deadline, self.amount_cents)


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_cents = models.fields.BigIntegerField('amount in cents')

    def __repr__(self):
        return "Payment(invoice={}, user={}, amount_cents={})" \
            .format(self.invoice, self.user, self.amount_cents)
