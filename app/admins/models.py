from django.db import models

# Create your models here.


class BaseRate(models.Model):
    name = models.CharField(max_length=36)
    charge = models.DecimalField(decimal_places=1, default=0.0, max_digits=9)
    vehicle_type = models.IntegerField(default=1)

    def __str__(self):
        return self.name


class DistanceCharge(models.Model):
    charge = models.DecimalField(decimal_places=1, default=0.0, max_digits=9)

    def __str__(self):
        return str(self.charge)


class Commission(models.Model):
    class Meta:
        verbose_name_plural = "Commission"

    commission = models.DecimalField(decimal_places=2, default=0.00, max_digits=9)

    def __str__(self):
        return str(self.commission)


class VAT(models.Model):
    class Meta:
        verbose_name_plural = "VAT"

    charge = models.DecimalField(decimal_places=2, default=0.00, max_digits=9)

    def __str__(self):
        return str(self.charge)


class Discount(models.Model):
    class Meta:
        verbose_name_plural = "Discount"

    discount = models.DecimalField(max_digits=9, decimal_places=1, default=0.0)

    def __str__(self):
        return str(self.discount)


class ProximityRadius(models.Model):
    radius = models.IntegerField(default=10)

    class Meta:
        verbose_name_plural = "Proximity Radius"

    def __str__(self):
        return str(self.radius)
