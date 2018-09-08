from django.db.models import Q, F
from django.shortcuts import render
from rest_framework import viewsets

from payments.models import Invoice, Payment
from payments.serializers import InvoiceSerializer, PaymentSerializer


def index(request):
    if request.user.is_authenticated:
        groups = request.user.groups.all().values_list('id', 'name')
        group_ids = [g[0] for g in groups]

        invoices_paid = Invoice.objects \
            .filter(groups__in=group_ids,
                    payment__user_id=request.user.id,
                    payment__amount_cents=F('amount_cents')) \
            .distinct() \
            .values('id', 'name', 'description', 'date_added', 'date_deadline',
                    'amount_cents', 'payment__user_id', 'payment__amount_cents')

        invoices_unpaid = Invoice.objects \
            .filter(Q(payment__amount_cents__lt=F('amount_cents')) |
                    Q(payment__amount_cents__isnull=True),
                    groups__in=group_ids) \
            .distinct() \
            .values('id', 'name', 'description', 'date_added', 'date_deadline',
                    'amount_cents')

        # The invoice may have matched with someone else's payment
        for i, inv in enumerate(invoices_unpaid):
            inv['payment__user_id'] = request.user.id
            payment = Payment.objects \
                .filter(invoice_id=inv['id'], user_id=request.user.id) \
                .values()
            if payment.first() is None:
                inv['payment__amount_cents'] = 0
            else:
                inv['payment__amount_cents'] = payment.first()['amount_cents']

        invoices_overpaid = Invoice.objects \
            .filter(groups__in=group_ids,
                    payment__user_id=request.user.id,
                    payment__amount_cents__gt=F('amount_cents')) \
            .distinct() \
            .values('id', 'name', 'description', 'date_added', 'date_deadline',
                    'amount_cents', 'payment__user_id', 'payment__amount_cents')

        data = {'username': request.user.email,
                'invoices': {
                    'paid': list(invoices_paid),
                    'unpaid': list(invoices_unpaid),
                    'overpaid': list(invoices_overpaid),
                },
                'groups': groups}
        return render(request, 'payments/invoices.html', data)
    else:
        return render(request, 'payments/notloggedin.html')


# REST API VIEWS

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
