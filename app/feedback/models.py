from django.db import models
import datetime

from users.models import User


class DriverRating(models.Model):
    driver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="driver_rating"
    )
    ratings = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="rating_owner"
    )
    created_at = models.DateField(default=datetime.date.today, blank=True)

    def __str__(self):
        return f"{self.driver.first_name} {self.driver.last_name}"
