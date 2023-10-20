from django.contrib import admin

from .models import Order, Earnings, RequestEarnings, Payment, DriverBankingInformation


class OrderAdmin(admin.ModelAdmin):
    list_filter = ("status",)


admin.site.register(Order, OrderAdmin)
admin.site.register(Earnings)
admin.site.register(RequestEarnings)
admin.site.register(Payment)
admin.site.register(DriverBankingInformation)
