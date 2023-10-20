import pytest
from django.contrib.auth import get_user_model, authenticate
from django.test import Client, TestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse
from rest_framework import status
from custom_auth.models import CustomOTP
from ..models import Bookings

User = get_user_model()


class TestBookingAuthenticated(TestCase):
    """Test Booking created, modified, and retrieved"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            phonenumber="0757660210",
        )
        self.otp = CustomOTP.objects.create(
            user=self.user, phonenumber="0757660210", otp="1234"
        )
        self.booking = Bookings.objects.create(owner=self.user)

        self.url = reverse("booking")

    def authenticate_user(self):
        payload = {"phonenumber": "0757660210", "otp": "1234"}
        auth_response = self.client.post(reverse("otp_confirm"), payload)
        token = auth_response.data["key"]
        self.client.defaults["HTTP_AUTHORIZATION"] = "Token {}".format(token)

    def test_get_created_booking_by_authenticated_user(self):
        """Test retrieving of a created booking"""
        self.authenticate_user()
        response = self.client.get(
            self.url,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["owner"]["email"], self.user.email)

    def test_booking_created_by_authenticated_user(self):
        """Test booking is created with booking ID"""
        self.authenticate_user()
        payload = {"owner": 1}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data["booking_id"])

    def test_booking_not_authenticated(self):
        """Test retrieving of a booking without being authenticated"""
        payload = {"owner": 1}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_modify_booking_details(self):
        """Test modification of booking details"""
        self.authenticate_user()
        payload = {
            "id": self.booking.id,
            "formated_address": "Test Address",
            "otp": "2342",
        }
        response = self.client.patch(
            self.url, payload, format="json", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        {
            self.assertEqual(response.data[key], payload[key])
            for key, value in payload.items()
        }
