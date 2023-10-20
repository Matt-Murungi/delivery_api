from firebase_admin.messaging import Notification, Message
from fcm_django.models import FCMDevice


class OrderStatus:
    CREATED = "1"
    CONFIRMED = "2"
    PICKED = "3"
    TRANSIT = "4"
    ARRIVED = "5"
    PARTNER_CREATED = "6"
    PARTNER_CONFIRMED = "7"
    REJECTED = "8"


def send_fcm_notification(user, title, body):
    device = FCMDevice.objects.filter(user=user).first()
    device.send_message(
        Message(notification=Notification(title=f"{title}", body=f"{body}"))
    )


def send_fcm_notification_to_partner(partner, title, body):
    device = FCMDevice.objects.get(user=partner)
    device.send_message(
        Message(notification=Notification(title=f"{title}", body=f"{body}"))
    )


def translate_order(order_number):
    if order_number is OrderStatus.CREATED:
        return "Your order has been created"
    if order_number is OrderStatus.CONFIRMED:
        return "Your order has been confirmed"
    if order_number is OrderStatus.PICKED:
        return "Your order has been picked by driver"
    if order_number is OrderStatus.TRANSIT:
        return "Your order is on it's way"
    if order_number is OrderStatus.ARRIVED:
        return "Your order has arrived"
    if order_number is OrderStatus.PARTNER_CREATED:
        return "Your order has been sent"
    if order_number is OrderStatus.PARTNER_CONFIRMED:
        return "Your order has been confirmed"
    if order_number is OrderStatus.REJECTED:
        return "Your order has been rejected"
