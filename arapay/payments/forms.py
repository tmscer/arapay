from django import forms

from payments.models import Invoice, User


class InvoiceSelectForm(forms.Form):
    invoice_select = forms.ModelChoiceField(Invoice.objects.order_by('-date_added'))


class UserSelectForm(forms.Form):
    user_select = forms.ModelChoiceField(User.objects.order_by('-last_name'))
