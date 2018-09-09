from django.urls import path, include
from rest_framework import routers

from payments.views import InvoiceViewSet, PaymentViewSet
from . import views

app_name = 'payments'

# REST Api
router = routers.DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('gen-var-sym/<int:invoice_id>/', views.generate_var_symbol, name='generate_var_symbol'),
    path('api/', include(router.urls), name='api')
]
