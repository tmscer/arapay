from django.http import HttpResponse
from rest_framework import viewsets

from payments.models import Invoice, Payment
from payments.serializers import InvoiceSerializer, PaymentSerializer


def index(request):
    if request.user.is_authenticated:
        return HttpResponse("Hello <b>%s</b>" % request.user.email)
    else:
        return HttpResponse("Hello World!<br><a href='%s'><button>Login</button></a>" % '/login')


# REST API VIEWS

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
