import random

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from rest_framework import viewsets

from payments import helpers
from payments.models import Invoice, Payment
from payments.serializers import InvoiceSerializer, PaymentSerializer


def index(request):
    if not request.user.is_authenticated:
        return render(request, 'payments/base.html')
    groups = request.user.groups.all().values()

    invoices_paid, invoices_unpaid, invoices_overpaid = helpers.invoices_paid_unpaid_overpaid(request.user)

    data = {'user': request.user,
            'invoices': {
                'paid': invoices_paid,
                'unpaid': invoices_unpaid,
                'overpaid': invoices_overpaid,
            },
            'groups': list(groups),
            'account_number': '285621010/0300',
            'currency': 'CZK'}
    return render(request, 'payments/invoices.html', data)


def by_user(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    groups = request.user.groups.all().values()
    users = User.objects.order_by('last_name')

    user_invoices = {}
    for user in users:
        user_key = (user.id, user.email)
        invoices_paid, invoices_unpaid, invoices_overpaid = helpers.invoices_paid_unpaid_overpaid(user)
        user_invoices[user_key] = {
            'paid': invoices_paid,
            'unpaid': invoices_unpaid,
            'overpaid': invoices_overpaid,
        }

    data = {'user': request.user,
            'user_invoices': user_invoices,
            'groups': list(groups),
            'account_number': '285621010/0300',
            'currency': 'CZK'}
    return render(request, 'payments/invoices-by-user.html', data)


def by_invoice(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    groups = request.user.groups.all().values()

    invoice_users = {}

    for invoice in Invoice.objects.order_by('-date_added'):
        stats = {'total_users': 0,
                 'n_paid': 0,
                 'n_unpaid': 0,
                 'n_overpaid': 0,
                 'amount_cents_paid': 0,
                 'amount_cents_owed': 0}
        groups = invoice.groups.all()
        users = User.objects.filter(groups__in=groups) \
            .order_by('last_name')
        stats['total_users'] = len(users)
        stats['amount_cents_owed'] = stats['total_users'] * invoice.amount_cents
        invoice_key = (invoice.id, invoice.name, invoice.amount_cents, invoice.date_added, invoice.date_deadline)
        current_users = {}
        for user in users:
            user_key = (user.id, user.email)
            payment = invoice.payment_set \
                .get_or_create(invoice_id=invoice.id,
                               user_id=user.id)[0]
            stats['amount_cents_paid'] += payment.amount_cents
            payment_dict = payment.__dict__
            if invoice.amount_cents == payment.amount_cents:
                payment_dict['status'] = 'paid'
                stats['n_paid'] += 1
            elif invoice.amount_cents > payment.amount_cents:
                payment_dict['status'] = 'unpaid'
                stats['n_unpaid'] += 1
            else:
                payment_dict['status'] = 'overpaid'
                stats['n_overpaid'] += 1
            current_users[user_key] = payment_dict
        invoice_users[invoice_key] = current_users
        stats['amount_cents_paid_percentage'] = 100.0 * stats['amount_cents_paid'] / stats['amount_cents_owed']
        invoice_users[invoice_key]['stats'] = stats

    data = {'user': request.user,
            'invoices_user': invoice_users,
            'groups': list(groups),
            'account_number': '285621010/0300',
            'currency': 'CZK'}
    return render(request, 'payments/invoices-by-invoice.html', data)


def generate_var_symbol(request, user_id, invoice_id):
    print(user_id)
    if not request.user.is_authenticated or user_id != request.user.id and not request.user.is_superuser:
        return HttpResponseForbidden()
    groups = User.objects.filter(pk=user_id).get().groups.all().values()
    group_ids = [g['id'] for g in groups]
    invoice_result = Invoice.objects.filter(id=invoice_id, groups__in=group_ids)
    if len(invoice_result) != 0:
        invoice = invoice_result.get()
    else:
        return HttpResponse('{"error":"invoice.na"}')

    payment_query = Payment.objects.filter(invoice_id=invoice_id, user_id=user_id)
    if len(payment_query) == 0:
        payment = None
    else:
        payment = payment_query.get()

    def gen_var_symbol():
        vs = random.randint(100000, 999999)
        while len(Payment.objects.filter(var_symbol=vs)) > 0:
            vs = random.randint(100000, 999999)
        return vs

    if payment is None:
        # Create it
        payment = Payment.objects.create(invoice_id=invoice_id,
                                         user_id=user_id,
                                         amount_cents=0,
                                         var_symbol=gen_var_symbol())
    elif payment.amount_cents == invoice.amount_cents:
        return HttpResponse('{"error":"paid"}')
    elif payment.amount_cents > invoice.amount_cents:
        return HttpResponse('{"error":"overpaid"}')
    elif payment.var_symbol != 0:
        return HttpResponse('{"error":"var_symbol.exists"}')
    else:
        # Var symbol has length 6
        payment.var_symbol = gen_var_symbol()
        payment.save()
    return HttpResponse('{"var_symbol":%s}' % payment.var_symbol)


# REST API VIEWS

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
