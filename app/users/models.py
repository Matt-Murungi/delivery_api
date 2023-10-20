import os

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db import models

from rest_framework.authtoken.models import Token
from twilio.rest import Client
from partners.models import Partner


account_sid = os.environ.get("ACCOUNT_SID")
auth_token = os.environ.get("AUTH_TOKEN")
sms_sender = os.environ.get("SMS_SENDER")
client = Client(account_sid, auth_token)


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phonenumber, password=None):
        if not email:
            raise ValueError("Users must have an email address!")
        if not first_name:
            raise ValueError("Users must have a first name!")
        if not last_name:
            raise ValueError("Users must have a last name!")
        if not phonenumber:
            raise ValueError("Users must have a phonenumber!")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phonenumber=phonenumber,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, first_name, last_name, phonenumber, password=None, **extra_fields
    ):
        user = self.create_user(email, first_name, last_name, phonenumber)
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=207, null=True, blank=True)
    last_name = models.CharField(max_length=207, null=True, blank=True)
    image = models.ImageField(upload_to="users/%Y/%m", default="users.png")
    phonenumber = models.CharField(max_length=17, null=False, blank=False, unique=True)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, null=True, blank=True, default="")
    is_admin = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phonenumber"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def get_number(self):
        return self.phonenumber

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_owner")
    is_approved = models.BooleanField(default=False)
    driving_license = models.FileField(
        upload_to="driving_license/%Y/%m", null=True, blank=True
    )
    insurance = models.FileField(upload_to="insurance/%Y/%m", null=True, blank=True)

    def __str__(self):
        return self.user.email


class OTP(models.Model):
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,10}$",
        message="Phone number must be entered in the format +254700000000. Up to 14 digits allowed.",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phonenumber = models.CharField(
        validators=[phone_regex], max_length=17, blank=False, null=True
    )
    otp = models.CharField(max_length=9, blank=True, null=True)
    count = models.IntegerField(default=0, help_text="Number of otp_sent")
    is_validated = models.BooleanField(
        default=False,
        help_text="If it is true, that means user have validate otp correctly in second API",
    )

    def __str__(self):
        return self.phonenumber

    def send_otp(self, otp):
        self.count += 1
        self.otp = otp
        self.save()
        message = client.messages.create(
            body=f"Hello, your otp confirmation code is {otp}",
            from_=sms_sender,
            to=self.phonenumber,
        )
        return otp


class DriverLocation(models.Model):
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    formated_address = models.CharField(
        null=True,
        blank=True,
        max_length=207,
    )

    def __str__(self):
        return self.owner.email


@receiver(post_save, sender=get_user_model())
def create_token(sender, instance, created, *args, **kwargs):
    if created:
        Token.objects.create(user=instance)
        Profile.objects.create(user=instance)
