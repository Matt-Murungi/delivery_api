from datetime import datetime
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import BaseModel


class Images(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    media = models.FileField(upload_to="general_images/%Y/%m")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Images"
        verbose_name_plural = "Images"

    def __str__(self):
        return self.media


PARTNER_SECTORS = (
    ("1", "Fashion"),
    ("2", "Bakery"),
    ("3", "Pharmacy"),
    ("4", "Supermarket"),
    ("5", "Manufacturing"),
    ("6", "Restaurants"),
)


class Partner(BaseModel):
    name = models.CharField(max_length=207, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    sector = models.CharField(choices=PARTNER_SECTORS, default=1, max_length=1)
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="partners/%Y/%m", null=True, blank=True)
    open_at = models.TimeField(blank=True, null=True)
    close_at = models.TimeField(blank=True, null=True)

    images = GenericRelation(Images, related_query_name="partner_images")

    def __str__(self):
        return self.name

    def is_partner_available(self):
        current_time = datetime.now().time()
        if current_time > self.close_at or current_time < self.open_at:
            return False
        return True


class ProductCategory(BaseModel):
    class Meta:
        verbose_name_plural = "ProductCategories"

    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, null=True, blank=True, default=""
    )
    name = models.CharField(max_length=207, null=True, blank=True)

    def __str__(self):
        return self.name


class PartnerProduct(BaseModel):
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, null=True, blank=True, default=""
    )
    name = models.CharField(max_length=207, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, null=True, blank=True, default=""
    )
    image = models.ImageField(upload_to="partner_products", null=True, blank=True)
    price = models.FloatField(default=0.0)

    def __str__(self):
        return self.name
