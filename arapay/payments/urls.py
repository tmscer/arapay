from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.index, name='index'),
    path('by_user/', views.by_user, name='by_user'),
    path('invoice/', views.get_invoice, name='invoice'),
    path('gen-var-sym/<int:user_id>/<int:invoice_id>/', views.generate_var_symbol, name='generate_var_symbol'),
    path('change_payment_status/<int:user_id>/<int:payment_id>/', views.change_payment_status, name='change_payment_status'),
]
