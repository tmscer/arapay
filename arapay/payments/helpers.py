from django.utils.encoding import escape_uri_path

from payments.models import Invoice


def invoices_paid_unpaid_overpaid(user):
    invoices_paid = []
    invoices_unpaid = []
    invoices_overpaid = []

    invoices_result = Invoice.objects \
        .filter(groups__in=user.groups.all()) \
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
