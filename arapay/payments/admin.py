from django.contrib import admin

# Register your models here.
from payments.models import Invoice, Payment, AccountInfo

admin.site.register(Invoice)
admin.site.register(Payment)
admin.site.register(AccountInfo)
