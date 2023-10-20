from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from partners.models import Images
from users.models import User

VEHICLE_TYPES = (("1", "Motorbike"), ("2", "Vehicle"), ("3", "Van"), ("4", "Truck"))


class Vehicle(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="vehicle_owner"
    )
    reg_number = models.CharField(max_length=10)
    vehicle_type = models.CharField(choices=VEHICLE_TYPES, default=1, max_length=1)
    model = models.CharField(max_length=45, blank=True, null=True)
    color = models.CharField(max_length=45, blank=True, null=True)
    insurance_expiry = models.DateTimeField(auto_now_add=True)

    images = GenericRelation(Images, related_query_name="vehicle_images")

    def __str__(self):
        return self.reg_number
