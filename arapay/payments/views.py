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
    users = User.objects.all()

    user_invoices = {}
    for user in users.values():
        user_key = (user['id'], user['email'])
        user_invoices[user_key] = {}
        invoices_paid, invoices_unpaid, invoices_overpaid = helpers.invoices_paid_unpaid_overpaid(
            users.get(pk=user['id']))
        user_invoices[user_key]['paid'] = invoices_paid
        user_invoices[user_key]['unpaid'] = invoices_unpaid
        user_invoices[user_key]['overpaid'] = invoices_overpaid

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

    invoices = Invoice.objects.all().values('id', 'name', 'amount_cents')
    invoice_users = {}

    for invoice in invoices:
        igroups = Invoice.objects.filter(pk=invoice['id']).get().groups.all().values('id')
        users = User.objects.filter(groups__in=igroups).values('id', 'email')
        invoice_key = (invoice['id'], invoice['name'], invoice['amount_cents'])
        current_users = {}
        for user in users:
            user_key = (user['id'], user['email'])
            payment = Payment.objects \
                .filter(invoice_id=invoice['id'], user_id=user['id']) \
                .values().first()
            if payment is None:
                payment = {
                    'amount_cents': 0,
                }
                if invoice['amount_cents'] < 0:
                    payment['status'] = 'overpaid'
                else:
                    payment['status'] = 'unpaid'
            elif invoice['amount_cents'] > payment['amount_cents']:
                payment['status'] = 'unpaid'
            elif invoice['amount_cents'] == payment['amount_cents']:
                payment['status'] = 'paid'
            else:
                payment['status'] = 'overpaid'
            current_users[user_key] = payment
        invoice_users[invoice_key] = current_users

    print(invoice_users)
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
