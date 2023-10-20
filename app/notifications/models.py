from django.db import models

from users.models import User
from core.models import BaseModel

class PeopleOnline(models.Model):
    online = models.ManyToManyField(to=User, blank=True)

    class Meta:
        verbose_name_plural = "People Online"

    def __str__(self):
        return str(self.id)


class Notification(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=10)

    def __str__(self):
        return self.owner.email


class OnlineDrivers(BaseModel):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    formated_address = models.CharField(
        null=True,
        blank=True,
        max_length=207,
    )

    class Meta:
        verbose_name_plural = "Online Drivers"

    def __str__(self):
        return self.driver.email
