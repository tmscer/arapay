import json
import random

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from payments import helpers
from payments.forms import InvoiceSelectForm, UserSelectForm
from payments.helpers import qr_code_url
from payments.models import Invoice, Payment
from payments.popo import InvoiceStats

from datetime import datetime as dt


@require_GET
def index(request):
    if not request.user.is_authenticated:
        return render(request, 'payments/base.html')
    groups = request.user.groups.all().values()

    invoices_paid, invoices_unpaid, invoices_overpaid = helpers.invoices_paid_unpaid_overpaid(request.user)

    data = {
        'user': request.user,
        'invoices': {
            'paid': invoices_paid,
            'unpaid': invoices_unpaid,
            'overpaid': invoices_overpaid,
        },
        'groups': list(groups),
        'currency': 'CZK'
    }
    return render(request, 'payments/invoices.html', data)


def by_user(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    users = []
    if request.method == 'POST':
        form = UserSelectForm(request.POST)
        if form.is_valid():
            # Show User
            try:
                user = User.objects.get(pk=form['user_select'].value())
            except Invoice.DoesNotExist:
                return HttpResponseNotFound()
            users = [user]
    else:
        form = UserSelectForm()

    data = helpers.user_invoice_view(request, users)
    data['form'] = form
    return render(request, 'payments/invoices-user.html', data)


def get_invoice(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    invoices = []
    if request.method == 'POST':
        form = InvoiceSelectForm(request.POST)
        if form.is_valid():
            # Show Invoice
            try:
                invoice = Invoice.objects.get(pk=form['invoice_select'].value())
            except Invoice.DoesNotExist:
                return HttpResponseNotFound()
            invoices = [invoice]
    else:
        form = InvoiceSelectForm()

    data = helpers.invoice_view(request, invoices)
    data['form'] = form
    return render(request, 'payments/invoices-invoices.html', data)


@require_POST
def change_payment_status(request, user_id, payment_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponseForbidden()
    try:
        payment = Payment.objects.get(id=payment_id, user=user_id)
    except Payment.DoesNotExist:
        return HttpResponseNotFound()
    invoice = payment.invoice
    if payment.amount_cents == invoice.amount_cents:
        payment.amount_cents = 0
        payment.date_paid = None
        previous = 'PAID'
        status = 'UNPAID'
    else:
        payment.amount_cents = invoice.amount_cents
        payment.date_paid = dt.now()
        status = 'PAID'
        previous = 'UNPAID'
    payment.save()
    return HttpResponse(json.dumps({'status': status, 'previous': previous}))


@require_POST
def generate_var_symbol(request, user_id, invoice_id):
    if not request.user.is_authenticated or (user_id != request.user.id and not request.user.is_staff):
        return HttpResponseForbidden()

    user = User.objects.get(id=user_id)
    invoice_result = Invoice.objects.filter(id=invoice_id)

    if invoice_result:
        invoice = invoice_result.get()
    else:
        return HttpResponse('{"error":"invoice.na"}')

    payment = invoice.payment_set \
        .get_or_create(invoice_id=invoice_id, user_id=user_id)[0]

    def gen_var_symbol():
        vs = 10 ** 7 + random.randint(10 ** 5, 10 ** 6 - 1)
        while Payment.objects.filter(var_symbol=vs):
            vs = 10 ** 7 + random.randint(10 ** 5, 10 ** 6 - 1)
        return vs

    if payment.amount_cents == invoice.amount_cents:
        return HttpResponse('{"error":"paid"}')
    elif payment.amount_cents > invoice.amount_cents:
        return HttpResponse('{"error":"overpaid"}')
    elif payment.var_symbol != 0:
        return HttpResponse('{"error":"var_symbol.exists"}')
    else:
        payment.var_symbol = gen_var_symbol()
        payment.save()
    response = {
        'var_symbol': str(payment.var_symbol),
        'url': qr_code_url(invoice, payment, user)
    }
    return HttpResponse(json.dumps(response))
