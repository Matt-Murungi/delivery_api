import os
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models
from django.utils.timezone import now
from geopy import distance
from twilio.rest import Client

from admins.models import (
    BaseRate,
    DistanceCharge,
    Commission,
    Discount,
    VAT,
)

from users.models import User
from .utils import generate_booking_id
from custom_auth.utils import generate_otp
from partners.models import Partner

account_sid = os.environ.get("ACCOUNT_SID")
auth_token = os.environ.get("AUTH_TOKEN")
sms_sender = os.environ.get("SMS_SENDER")
client = Client(account_sid, auth_token)


VEHICLE_TYPES = (("1", "Motorbike"), ("2", "Vehicle"), ("3", "Van"), ("4", "Truck"))

PAYMENT_TYPES = (("1", "Cash"), ("2", "MPESA"), ("3", "Card"))


class Bookings(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_id = models.CharField(max_length=12, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    formated_address = models.CharField(
        null=False,
        blank=False,
        max_length=207,
        default="Unknown Location",
    )
    otp = models.CharField(max_length=5, null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, null=True, blank=True, default=""
    )
    vehicle_type = models.CharField(choices=VEHICLE_TYPES, default=1, max_length=1)
    payment_type = models.CharField(choices=PAYMENT_TYPES, default=1, max_length=1)
    scheduled_date = models.DateTimeField(blank=True, null=True, default=now)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Bookings"

    def __str__(self):
        return self.booking_id

    def get_amount_range(self):
        base_rates = BaseRate.objects.all()
        sender_lat = self.latitude
        sender_long = self.longitude
        sender_position = (sender_lat, sender_long)
        if sender_lat is None or sender_long is None:
            msg = "Sender's location not specified, please update the order."
            return msg

        receiver_lat = self.booking_receiver.all().first().latitude
        receiver_long = self.booking_receiver.all().first().longitude
        receiver_position = (receiver_lat, receiver_long)

        if receiver_lat is None or receiver_long is None:
            msg = "Receiver's location not specified, please update the order."
            return msg

        calculated_distance = distance.distance(sender_position, receiver_position).km
        distance_charge = DistanceCharge.objects.all().first()
        commision = float(Commission.objects.all().first().commission)
        vat = float(VAT.objects.all().first().charge)
        discount = float(Discount.objects.all().first().discount)
        commision = float(Commission.objects.all().first().commission)
        distance_total = float(distance_charge.charge) * calculated_distance

        amount_range = dict()
        for base_rate in base_rates:
            driver_fee = float(base_rate.charge) + distance_total
            bdeliv_commission = commision + driver_fee
            tax = (bdeliv_commission + driver_fee) * vat

            amount_range[base_rate.name] = round(
                (driver_fee + commision + tax) - discount, 1
            )

        return amount_range

    def send_otp(self):
        otp = generate_otp()
        self.otp = otp
        booking_receiver = self.booking_receiver.all().first()
        client.messages.create(
            body=f"Hello, your booking reception confirmation code is {otp}.",
            from_=sms_sender,
            to=booking_receiver.phonenumber,
        )
        self.save()
        return otp


class ReceiverDetails(models.Model):
    booking = models.ForeignKey(
        Bookings, on_delete=models.CASCADE, related_name="booking_receiver"
    )
    name = models.CharField(max_length=207)
    phonenumber = models.CharField(max_length=15)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    formated_address = models.CharField(
        null=False,
        blank=False,
        max_length=207,
        default="Unknown Location",
    )

    class Meta:
        verbose_name_plural = "Receiver Details"

    def __str__(self):
        return self.name


PRODUCT_TYPES = (
    ("1", "ELectronics"),
    ("2", "Gift"),
    ("3", "Document"),
    ("4", "Package"),
    ("5", "Food"),
    ("6", "Other"),
)


class Products(models.Model):
    booking = models.ForeignKey(
        Bookings, on_delete=models.CASCADE, related_name="booking_product"
    )
    product_type = models.CharField(
        max_length=1,
        choices=PRODUCT_TYPES,
        default=6,
    )
    name = models.CharField(max_length=207, blank=True, null=True)
    quantity = models.CharField(max_length=207, blank=True, null=True)
    image = models.ImageField(upload_to="products", blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Products"

    def __str__(self):
        return self.booking.booking_id


# generate booking_id before saving
@receiver(pre_save, sender=Bookings)
def create_booking_id(sender, instance, *args, **kwargs):
    if not instance.booking_id:
        instance.booking_id = generate_booking_id(instance)
