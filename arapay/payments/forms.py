from django import forms

from payments.models import Invoice


class InvoiceSearchForm(forms.Form):
    invoice_select = forms.ModelChoiceField(Invoice.objects.order_by('-date_added'))
