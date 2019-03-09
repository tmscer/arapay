import json
import random

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from payments import helpers
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


@require_GET
def by_user(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    groups = request.user.groups.all().values()
    users = User.objects.order_by('email')

    user_invoices = {}
    for user in users:
        user_key = (user.id, user.email, user.username)
        invoices_paid, invoices_unpaid, invoices_overpaid = helpers.invoices_paid_unpaid_overpaid(user)
        stats = InvoiceStats(user.id, len(invoices_paid) + len(invoices_unpaid) + len(invoices_overpaid))
        stats.n_paid = len(invoices_paid)
        stats.n_unpaid = len(invoices_unpaid)
        stats.n_overpaid = len(invoices_overpaid)
        for invoice in invoices_paid + invoices_unpaid + invoices_overpaid:
            stats.amount_cents_owed += invoice.amount_cents
            stats.amount_cents_paid += invoice.payment_set.get(user_id=user.id).amount_cents
        user_invoices[user_key] = {
            'paid': invoices_paid,
            'unpaid': invoices_unpaid,
            'overpaid': invoices_overpaid,
            'stats': stats.as_dict(),
        }

    data = {
        'user': request.user,
        'user_invoices': user_invoices,
        'groups': list(groups),
        'currency': 'CZK'
    }
    return render(request, 'payments/invoices-by-user.html', data)


@require_GET
def by_invoice(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    groups = request.user.groups.all().values()

    invoice_users = {}
    stats_all = {}

    for invoice in Invoice.objects.order_by('-date_added'):
        users = User.objects \
            .filter(Q(groups__in=invoice.groups.all().values_list('id', flat=True)) |
                    Q(id__in=invoice.users.all().values_list('id', flat=True))) \
            .distinct() \
            .order_by('email')
        stats = InvoiceStats(invoice.id, len(users))
        stats.amount_cents_owed = stats.n_total * invoice.amount_cents
        current_users = {}
        for user in users:
            payment = invoice.payment_set.get_or_create(invoice=invoice, user=user)[0].__dict__
            stats.amount_cents_paid += payment['amount_cents']
            if invoice.amount_cents == payment['amount_cents']:
                payment['status'] = 'paid'
                stats.n_paid += 1
            elif invoice.amount_cents > payment['amount_cents']:
                payment['status'] = 'unpaid'
                stats.n_unpaid += 1
            else:
                payment['status'] = 'overpaid'
                stats.n_overpaid += 1
            current_users[(user.id, user.email)] = payment
        invoice_users[(invoice.id, invoice.name,
                       invoice.amount_cents, invoice.date_added, invoice.date_deadline)] = current_users
        stats_all[invoice.id] = stats.as_dict()

    data = {
        'user': request.user,
        'invoices_user': invoice_users,
        'stats_all': stats_all,
        'groups': list(groups),
        'currency': 'CZK'
    }
    return render(request, 'payments/invoices-by-invoice.html', data)


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
