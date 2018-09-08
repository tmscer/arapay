from django.contrib import admin

# Register your models here.
from payments.models import Invoice, Payment

admin.site.register(Invoice)
admin.site.register(Payment)
