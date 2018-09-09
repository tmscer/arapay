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

    data = {'username': request.user.email,
            'invoices': {
                'paid': invoices_paid,
                'unpaid': invoices_unpaid,
                'overpaid': invoices_overpaid,
            },
            'groups': list(groups)}
    return render(request, 'payments/invoices.html', data)


# REST API VIEWS

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
