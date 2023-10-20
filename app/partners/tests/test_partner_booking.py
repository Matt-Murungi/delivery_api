from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from ..models import Partner

User = get_user_model()


class TestPartnerBookings(TestCase):
    """Test the booking process made by a user belonging to a partner"""

    def setUp(self):
        self.partner = Partner.objects.create(
            name="test_partner"
        )

        self.user = User.objects.create_user(
            email="testpartner@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            phonenumber="0757660210",
        )
        