from django.contrib import admin

from .models import CustomOTP, PreassignedOTP

admin.site.register(CustomOTP)
admin.site.register(PreassignedOTP)
