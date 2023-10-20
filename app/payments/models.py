from channels.layers import get_channel_layer
from datetime import date
from geopy import distance
import math

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

from asgiref.sync import async_to_sync

# from datetime import date, datetime, timedelta
from django.utils import timezone

from bookings.models import Bookings, ReceiverDetails
from users.models import User
from fcm_django.models import FCMDevice

# from users.serializers import UserSerializer
from vehicles.models import Vehicle

# from vehicles.serializers import VehicleSerializer
from notifications.serializers import Notification, NotificationSerializer

from .commands import (
    send_fcm_notification,
    translate_order,
    send_fcm_notification_to_partner,
)


from admins.models import (
    DistanceCharge,
    BaseRate,
    ProximityRadius,
    Commission,
    Discount,
    VAT,
)
from notifications.models import OnlineDrivers

channel_layer = get_channel_layer()

ORDER_STATUS = (
    ("1", "created"),
    ("2", "confirmed"),
    ("3", "picked"),
    ("4", "transit"),
    ("5", "arrived"),
    ("6", "partner_created"),
    ("7", "partner_confirmed"),
    ("8", "rejected"),
)

PAYMENT_STATUS = (("1", "Settled"), ("2", "Refunded"))


class OrderManager(models.Manager):
    def get_available_orders(self, user):
        vehicles = Vehicle.objects.filter(owner=user)
        orders = self.model.objects.filter(driver=None).filter(status="1")
        orders_ = []
        for vehicle in vehicles:
            order_booking_vehicle = orders.filter(
                booking__vehicle_type=vehicle.vehicle_type
            ).distinct()
            for order in order_booking_vehicle:
                schedule_date = order.booking.scheduled_date
                if schedule_date is not None:
                    schedule_date = schedule_date.date()
                    # if schedule_date >= date.today():
                    #     orders_.append(order)
                    if schedule_date <= date.today():
                        time = order.booking.scheduled_date
                        order_local_time = timezone.localtime(time)
                        now = timezone.now()
                        local_time_now = timezone.localtime(now)
                        t1 = local_time_now
                        t2 = order_local_time
                        delta = t2 - t1
                        minutes_delta = delta / 60

                        if minutes_delta.total_seconds() <= 5:
                            orders_.append(order)
        return orders_


class Order(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="order_owner"
    )
    booking = models.ForeignKey(Bookings, on_delete=models.CASCADE)
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="order_driver",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_vehicle",
    )
    amount = models.DecimalField(max_digits=9, decimal_places=1, default=0.0)
    status = models.CharField(choices=ORDER_STATUS, default=1, max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    objects = OrderManager()

    def __str__(self):
        return self.owner.email

    def save(self, *args, **kwargs):
        # Check if the status has changed
        if self.pk:  # Only for existing orders
            original_order = Order.objects.get(pk=self.pk)
            if self.status != original_order.status:
                send_fcm_notification(
                    self.owner,
                    title=f"Hi {self.owner.first_name}",
                    body=translate_order(self.status),
                )
                if self.status == "6":
                    partner = User.objects.filter(partner=self.booking.partner).first()
                    send_fcm_notification_to_partner(
                        partner, self.status, partner.first_name
                    )
                if self.status == "1":
                    online_drivers = User.objects.filter(
                        is_driver=True, onlinedrivers__is_active=True
                    )
                    for driver in online_drivers:
                        send_fcm_notification(
                            driver, title="New order", body="You have a new order"
                        )
        super().save(*args, **kwargs)

    def get_booking_receiver(self):
        receiver = ReceiverDetails.objects.filter(booking=self.booking)[0]
        return receiver.name

    def update_order(self):
        price = 0.0
        vehicle_type = self.booking.vehicle_type

        if vehicle_type == 1:
            price = 150.0

        elif vehicle_type == 2:
            price = 200.0

        elif vehicle_type == 3:
            price = 300.0

        elif vehicle_type == 4:
            price = 400.0

        self.amount = math.floor(price)
        self.save()
        return self.amount

    def get_payment_charge(self):
        vehicle_type = self.booking.vehicle_type
        vehicle_charge = BaseRate.objects.filter(vehicle_type=vehicle_type).first()
        vehicle_charge_amount = vehicle_charge.charge

        sender_lat = self.booking.latitude
        sender_long = self.booking.longitude
        sender_position = (sender_lat, sender_long)

        receiver_lat = self.booking.booking_receiver.all().first().latitude
        receiver_long = self.booking.booking_receiver.all().first().longitude
        receiver_position = (receiver_lat, receiver_long)

        calculated_distance = distance.distance(sender_position, receiver_position).km
        distance_charge = DistanceCharge.objects.all().first()
        commision = float(Commission.objects.all().first().commission)
        vat = float(VAT.objects.all().first().charge)
        discount = float(Discount.objects.all().first().discount)
        distance_total = float(distance_charge.charge) * calculated_distance
        driver_fee = float(vehicle_charge_amount) + distance_total
        bdeliv_commision = commision * driver_fee
        tax = vat * (driver_fee + bdeliv_commision)
        amount = (driver_fee + bdeliv_commision + tax) - discount

        self.amount = math.trunc(amount)
        self.save()
        return math.trunc(amount)

    def get_drivers(self):
        vehicle_type = self.booking.vehicle_type
        vehicles = Vehicle.objects.all().filter(vehicle_type=vehicle_type)
        online_drivers = OnlineDrivers.objects.all()
        latitude = self.booking.latitude
        longitude = self.booking.longitude
        sender_pos = (latitude, longitude)
        within_range = []
        for driver in online_drivers:
            driver_lat = driver.latitude
            driver_long = driver.longitude
            driver_pos = (driver_lat, driver_long)
            calculated_distance = distance.distance(sender_pos, driver_pos).km
            radius = ProximityRadius.objects.first().radius
            if calculated_distance < radius + 1:
                within_range.append(driver.driver.id)

        vehicles = vehicles.filter(owner__id__in=tuple(within_range))

        schedule_date = self.booking.scheduled_date.date()
        if not schedule_date == date.today():
            return

        order = {
            "id": self.id,
            "from": {
                "latitude": self.booking.latitude,
                "longitude": self.booking.longitude,
                "formated_address": self.booking.formated_address,
            },
            "receiver": {
                "name": self.booking.booking_receiver.all().first().name,
                "latitude": self.booking.booking_receiver.all().first().latitude,
                "longitude": self.booking.booking_receiver.all().first().longitude,
                "formated_address": self.booking.booking_receiver.all()
                .first()
                .formated_address,
            },
            "owner": {
                "name": f"{self.owner.first_name} {self.owner.last_name}",
                "phonenumber": f"{self.owner.phonenumber}",
            },
            "product": {
                "type": self.booking.booking_product.all().first().product_type,
                "instructions": self.booking.booking_product.all().first().instructions,
            },
            "pick_time": {
                "time": str(self.booking.scheduled_date),
            },
        }

        for vehicle in vehicles:
            vehicle_owner = vehicle.owner
            group_name = f"{vehicle_owner.id}__notifications"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "order_notifications",
                    "name": group_name,
                    "message": "An order is being created, will you accept",
                    "order": order,
                },
            )
        return vehicles


class Earnings(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=1, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Earnings"

    def __str__(self):
        return self.owner.email


@receiver(post_save, sender=Order)
def send_user_notification(sender, instance, created, *args, **kwargs):
    order = instance
    status = order.status
    owner = order.owner

    def send_user_notification(message):
        notification = Notification.objects.create(
            owner=owner, text=message, order_id=order.id
        )

        group_name = f"{owner.id}__notifications"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "order_notifications",
                "name": group_name,
                "notification": NotificationSerializer(notification).data,
            },
        )

    if status == 1:
        pass

    elif status == 2:
        driver = order.driver
        msg = {
            "detail": f"{driver.first_name} {driver.last_name} has confirmed the order",
        }
        send_user_notification(msg)

        send_fcm_notification(owner, title="Status", body="Updated")

    elif status == 3:
        msg = {"detail": "You package has been picked"}
        send_user_notification(msg)

    elif status == 4:
        msg = {"detail": "You package is in transit"}
        send_user_notification(msg)

    elif status == 5:
        receiver = order.get_booking_receiver()
        msg = {"detail": f"{receiver} has collected the package"}
        send_user_notification(msg)


class Payment(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="payment_owner",
        null=True,
        blank=True,
    )
    amount = models.FloatField(default=0.0)
    status = models.CharField(choices=ORDER_STATUS, default=1, max_length=1)
    transaction_id = models.CharField(max_length=108, null=True, blank=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_order",
    )
    card_code = models.CharField(max_length=108, null=True, blank=True)
    expiration_date = models.CharField(max_length=27, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.owner.email

    def send_user_payment_notification(self, order_id):
        group_name = f"{self.owner.id}__notifications"
        msg = f"Payment for order {order_id} has been confirmed"
        notification = Notification.objects.create(
            owner=self.owner, text=msg, order_id=order_id
        )
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "order_notifications",
                "name": group_name,
                "notification": NotificationSerializer(notification).data,
            },
        )

    def send_user_refund_notification(self, order_id):
        group_name = f"{self.owner.id}__notifications"
        msg = "Your payment has been refunded"
        notification = Notification.objects.create(
            owner=self.owner, text=msg, order_id=order_id
        )
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "order_notifications",
                "name": group_name,
                "notification": NotificationSerializer(notification).data,
            },
        )


REQUEST_STATUS = ((1, "Pending"), (2, "Paid"))


class RequestEarnings(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=1, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(choices=REQUEST_STATUS, max_length=1, default=1)

    class Meta:
        verbose_name_plural = "Request Earnings"

    def __str__(self):
        return self.owner.email


class DriverBankingInformation(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=50, null=True)
    bank_branch = models.CharField(max_length=50, null=True)
    account_name = models.CharField(max_length=70, null=True)
    account_number = models.BigIntegerField(null=True)
    # card_number = models.CharField(max_length=36)
    # card_code = models.CharField(max_length=3)
    # expiration_date = models.CharField(max_length=18)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.owner.email
