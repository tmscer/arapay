from payments.models import Invoice, Payment


def invoices_paid_unpaid_overpaid(request, user):
    groups = user.groups.all().values()
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
            if invoice['amount_cents'] < 0:
                invoices_overpaid.append(invoice)
            else:
                invoices_unpaid.append(invoice)
            continue
        invoice['payment'] = payment
        if invoice['amount_cents'] > payment['amount_cents']:
            invoices_unpaid.append(invoice)
        elif invoice['amount_cents'] == payment['amount_cents']:
            invoices_paid.append(invoice)
        else:
            invoices_overpaid.append(invoice)

    return invoices_paid, invoices_unpaid, invoices_overpaid
