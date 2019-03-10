from django.shortcuts import render
from django.utils.encoding import escape_uri_path

from payments.models import Invoice, User
from django.db.models import Q

from payments.popo import InvoiceStats


def invoice_view(request, invoices):
    groups = request.user.groups.all().values()
    invoice_users, stats_all = invoice_data(invoices)

    data = {
        'user': request.user,
        'invoices_user': invoice_users,
        'stats_all': stats_all,
        'groups': list(groups),
        'currency': 'CZK'
    }
    return data


def invoice_data(invoices):
    invoice_users = {}
    stats_all = {}
    for inv in invoices:
        users = User.objects \
            .filter(Q(groups__in=inv.groups.all().values_list('id', flat=True)) |
                    Q(id__in=inv.users.all().values_list('id', flat=True))) \
            .distinct() \
            .order_by('email')
        stats = InvoiceStats(inv.id, len(users))
        stats.amount_cents_owed = stats.n_total * inv.amount_cents
        current_users = {}
        for user in users:
            payment = inv.payment_set.get_or_create(invoice=inv, user=user)[0].__dict__
            stats.amount_cents_paid += payment['amount_cents']
            if inv.amount_cents == payment['amount_cents']:
                payment['status'] = 'paid'
                stats.n_paid += 1
            elif inv.amount_cents > payment['amount_cents']:
                payment['status'] = 'unpaid'
                stats.n_unpaid += 1
            else:
                payment['status'] = 'overpaid'
                stats.n_overpaid += 1
            current_users[(user.id, user.email)] = payment
        invoice_users[(inv.id, inv.name,
                       inv.amount_cents, inv.date_added, inv.date_deadline)] = current_users
        stats_all[inv.id] = stats.as_dict()
    return invoice_users, stats_all


def invoices_paid_unpaid_overpaid(user):
    invoices_paid = []
    invoices_unpaid = []
    invoices_overpaid = []

    invoices_result = Invoice.objects \
        .filter(Q(groups__in=user.groups.all()) | Q(users__in=[user])) \
        .distinct() \
        .order_by('-date_added')

    for invoice in invoices_result:
        payment = invoice.payment_set.get_or_create(invoice_id=invoice.id, user_id=user.id)[0]
        if payment.amount_cents == invoice.amount_cents:
            invoices_paid.append(invoice)
        elif payment.amount_cents < invoice.amount_cents:
            invoices_unpaid.append(invoice)
        else:
            invoices_overpaid.append(invoice)

    return invoices_paid, invoices_unpaid, invoices_overpaid


def url_args(args):
    return ''.join(("&%s=%s" % (key, escape_uri_path(str(value))) for key, value in args.items()))


def qr_code_url(invoice, payment, user):
    base_url = "https://api.paylibo.com/paylibo/generator/czech/image?compress=true&size=230"
    deadline = invoice.date_deadline
    args = {
        'accountNumber': invoice.account_info.account_number,
        'bankCode': invoice.account_info.bank_code,
        'currency': 'CZK',
        'vs': payment.var_symbol,
        'date': "{y}-{m}-{d}".format(y=deadline.year,
                                     m=deadline.month,
                                     d=deadline.day),
        'message': 'arapay-%s-%s' % (invoice.name, user.username),
        'amount': (invoice.amount_cents - payment.amount_cents) / 100
    }
    return base_url + url_args(args)
