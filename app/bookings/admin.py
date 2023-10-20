from django.contrib import admin

from .models import Bookings, ReceiverDetails, Products

admin.site.register(Bookings)
admin.site.register(ReceiverDetails)
admin.site.register(Products)
