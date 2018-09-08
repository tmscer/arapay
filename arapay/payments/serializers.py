from rest_framework import serializers

from payments.models import Payment, Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ('name', 'description', 'date_deadline', 'amount_cents', 'groups')


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('invoice', 'user', 'amount_cents')
