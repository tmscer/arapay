from django.template.defaulttags import register


@register.filter
def get_payment(invoice, user_id):
    return invoice.payment_set.get(user_id=user_id)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def make_tags(tag, items):
    return ''.join(("<%s>%s</%s>" % (tag, a, tag) for a in items.split(',')))


@register.filter
def amount_owed(invoice_amount_cents, payment_amount_cents):
    return (invoice_amount_cents - payment_amount_cents) / 100
