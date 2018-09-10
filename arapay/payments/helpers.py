from payments.models import Invoice, Payment


def invoices_paid_unpaid_overpaid(user):
    invoices_paid = []
    invoices_unpaid = []
    invoices_overpaid = []

    invoices_result = Invoice.objects.filter(groups__in=user.groups.all()).distinct()

    print(invoices_result)

    for invoice in invoices_result:
        payment = invoice.payment_set.get_or_create(invoice_id=invoice.id, user_id=user.id)[0]
        if payment.amount_cents == invoice.amount_cents:
            invoices_paid.append(invoice)
        elif payment.amount_cents < invoice.amount_cents:
            invoices_unpaid.append(invoice)
        else:
            invoices_overpaid.append(invoice)

    return invoices_paid, invoices_unpaid, invoices_overpaid
