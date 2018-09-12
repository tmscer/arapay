from django.template.defaulttags import register


@register.filter
def get_payment(invoice, user_id):
    return invoice.payment_set.get(user_id=user_id)
