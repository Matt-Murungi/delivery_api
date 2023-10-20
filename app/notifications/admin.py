from django.contrib import admin

from .models import PeopleOnline, Notification, OnlineDrivers

admin.site.register(PeopleOnline)
admin.site.register(Notification)
admin.site.register(OnlineDrivers)
