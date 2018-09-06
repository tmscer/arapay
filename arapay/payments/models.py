from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Invoice(models.Model):
    name = models.fields.CharField('invoice name', max_length=32)
    description = models.fields.TextField('payment description', max_length=200)
    date_added = models.fields.DateTimeField('date added')
    date_deadline = models.fields.DateTimeField('date due')
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


class Group(models.Model):
    name = models.fields.CharField('group name', max_length=32)


class UserToGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class InvoiceToGroup(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
