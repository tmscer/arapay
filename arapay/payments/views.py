import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets

from payments.models import Invoice, Payment
from payments.serializers import InvoiceSerializer, PaymentSerializer


def index(request):
    if not request.user.is_authenticated:
        return render(request, 'payments/notloggedin.html')
    groups = request.user.groups.all().values()
    group_ids = [g['id'] for g in groups]

    invoices_paid = []
    invoices_unpaid = []
    invoices_overpaid = []

    invoices_result = Invoice.objects \
        .filter(groups__in=group_ids) \
        .distinct() \
        .values('id', 'name', 'description', 'date_added', 'date_deadline', 'amount_cents')

    for invoice in invoices_result:
        payment = Payment.objects \
            .filter(invoice_id=invoice['id'], user_id=request.user.id) \
            .values().first()
        if payment is None:
            invoice['payment'] = {
                'amount_cents': 0,
                'user_id': request.user.id
            }
            invoices_unpaid.append(invoice)
            continue
        invoice['payment'] = payment
        if invoice['amount_cents'] > payment['amount_cents']:
            invoices_unpaid.append(invoice)
        elif invoice['amount_cents'] == payment['amount_cents']:
            invoices_paid.append(invoice)
        else:
            invoices_overpaid.append(invoice)

    data = {'user': request.user,
            'invoices': {
                'paid': invoices_paid,
                'unpaid': invoices_unpaid,
                'overpaid': invoices_overpaid,
            },
            'groups': list(groups),
            'account_number': '285621010/0300'}
    return render(request, 'payments/invoices.html', data)


@login_required
def generate_var_symbol(request, invoice_id):
    groups = request.user.groups.all().values()
    group_ids = [g['id'] for g in groups]
    invoice_result = Invoice.objects.filter(id=invoice_id, groups__in=group_ids)
    if len(invoice_result) != 0:
        invoice = invoice_result.get()
    else:
        return HttpResponse('{"error":"invoice.na"}')

    payment_query = Payment.objects.filter(invoice_id=invoice_id, user_id=request.user.id)
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
                                         user_id=request.user.id,
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
