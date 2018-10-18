import random

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.http import require_GET

from payments import helpers
from payments.models import Invoice, Payment
from payments.popo import InvoiceStats


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
        'account_number': '285621010/0300',
        'currency': 'CZK'
    }
    return render(request, 'payments/invoices.html', data)


@require_GET
def by_user(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    groups = request.user.groups.all().values()
    users = User.objects.order_by('last_name')

    user_invoices = {}
    for user in users:
        user_key = (user.id, user.email, user.username)
        invoices_paid, invoices_unpaid, invoices_overpaid = helpers.invoices_paid_unpaid_overpaid(user)
        user_invoices[user_key] = {
            'paid': invoices_paid,
            'unpaid': invoices_unpaid,
            'overpaid': invoices_overpaid,
        }

    data = {
        'user': request.user,
        'user_invoices': user_invoices,
        'groups': list(groups),
        'account_number': '285621010/0300',
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
            .filter(groups__in=invoice.groups.all().values_list('id', flat=True)) \
            .order_by('last_name')
        stats = InvoiceStats(invoice.id, len(users))
        stats.amount_cents_owed = stats.total_users * invoice.amount_cents
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
        'account_number': '285621010/0300',
        'currency': 'CZK'
    }
    return render(request, 'payments/invoices-by-invoice.html', data)


@require_GET
def generate_var_symbol(request, user_id, invoice_id):
    if not request.user.is_authenticated or (user_id != request.user.id and not request.user.is_staff):
        return HttpResponseForbidden()
    groups = User.objects.filter(pk=user_id).get().groups.all().values()
    group_ids = [g['id'] for g in groups]
    invoice_result = Invoice.objects.filter(id=invoice_id, groups__in=group_ids)
    if len(invoice_result) != 0:
        invoice = invoice_result.get()
    else:
        return HttpResponse('{"error":"invoice.na"}')

    payment = invoice.payment_set \
        .get_or_create(invoice_id=invoice_id, user_id=user_id)[0]

    def gen_var_symbol():
        vs = 10 ** 7 + random.randint(10 ** 5, 10 ** 6 - 1)
        while len(Payment.objects.filter(var_symbol=vs)) > 0:
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
    return HttpResponse('{"var_symbol":%s}' % payment.var_symbol)
