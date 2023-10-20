from django.contrib import admin

from .models import Partner, Images, PartnerProduct, ProductCategory

admin.site.register(Partner)
admin.site.register(Images)
admin.site.register(PartnerProduct)
admin.site.register(ProductCategory)
