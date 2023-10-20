import os

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

from core.models import BaseModel

from twilio.rest import Client

User = get_user_model()

account_sid = os.environ.get("ACCOUNT_SID")
auth_token = os.environ.get("AUTH_TOKEN")
sms_sender = os.environ.get("SMS_SENDER")
client = Client(account_sid, auth_token)


class CustomOTP(models.Model):
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
        help_text="If it is true, that means user has validated otp correctly in second API",
    )
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.phonenumber

    def send_otp(self, otp):
        message = client.messages.create(
            body=f"Hello, your OTP confirmation code is {otp}.",
            from_=sms_sender,
            to=self.phonenumber,
        )
        self.count += 1
        self.otp = otp
        self.is_validated = False
        self.save()
        return otp

    def check_expiry(self):
        pass


class PreassignedOTP(BaseModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phonenumber = models.CharField(
         max_length=17, blank=False, null=True
    )
    otp = models.CharField(max_length=9, blank=True, null=True)
    is_validated = models.BooleanField(
        default=False,
        help_text="If it is true, that means user has validated otp correctly in second API",
    )

    def __str__(self):
        return self.user.phonenumber
