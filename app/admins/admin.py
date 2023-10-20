from django.contrib import admin

from .models import BaseRate, DistanceCharge, \
    ProximityRadius, Discount, Commission, VAT

admin.site.register(BaseRate)
admin.site.register(DistanceCharge)
admin.site.register(Commission)
admin.site.register(VAT)
admin.site.register(Discount)
admin.site.register(ProximityRadius)
