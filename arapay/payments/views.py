from django.db.models import Q, F
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets

from payments.models import Invoice, Payment
from payments.serializers import InvoiceSerializer, PaymentSerializer


def index(request):
    if request.user.is_authenticated:
        groups = request.user.groups.all().values_list('id', 'name')
        group_ids = [g[0] for g in groups]
        values = 'name', 'description', 'date_added', 'date_deadline', 'amount_cents', 'payment__amount_cents'

        invoices_paid = Invoice.objects \
            .filter(groups__in=group_ids,
                    payment__user_id=request.user.id,
                    payment__amount_cents=F('amount_cents')) \
            .distinct() \
            .values(*values)

        invoices_unpaid = Invoice.objects \
            .filter(groups__in=group_ids) \
            .filter(Q(payment__amount_cents__isnull=True) | Q(payment__amount_cents__lt=F('amount_cents'))) \
            .distinct() \
            .values(*values)

        invoices_overpaid = Invoice.objects \
            .filter(groups__in=group_ids,
                    payment__user_id=request.user.id,
                    payment__amount_cents__gt=F('amount_cents')) \
            .distinct() \
            .values(*values)

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
