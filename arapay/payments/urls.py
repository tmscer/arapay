from django.urls import path, include
from rest_framework import routers

from payments.views import InvoiceViewSet, PaymentViewSet
from . import views

# REST Api
router = routers.DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls), name='api')
]
