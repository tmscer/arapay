from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_item2(dictionary, key1, key2):
    return dictionary.get((key1, key2))


@register.simple_tag
def get_payment(invoice, user_id):
    return {'payment': invoice.payment_set.get(user_id=user_id)}


@register.filter
def get_payment2(invoice, user_id):
    return invoice.payment_set.get(user_id=user_id)
