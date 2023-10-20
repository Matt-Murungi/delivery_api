from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_deleted and not self.date_deleted:
            self.date_deleted = timezone.now()
            self.is_active = False
        elif not self.is_deleted and self.date_deleted:
            self.date_deleted = None

        super().save(*args, **kwargs)
