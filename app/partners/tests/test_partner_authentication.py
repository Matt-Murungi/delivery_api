import pytest
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from ..models import Partner
from ..serializers import PartnerLoginSerializer, PartnerSerializer

User = get_user_model()


class TestPartnerAuthenticationView(TestCase):
    """Test partner authentication"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            phonenumber="0757660210",
        )
        self.partner = Partner.objects.create(name="test_partner")

    # def test_partner_authentication(self):
    #     # Define test data
    #     data = {"email": "test@example.com", "password": "testpassword"}

    #     url = reverse("partner-authentication")
    #     response = self.client.post(url, data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    #     expected_data = PartnerSerializer(self.partner).data
    #     self.assertEqual(response.data, [expected_data])

    def test_partner_authentication_view_missing_credentials(self):
        # Define test data with missing email and password
        data = {}

        url = reverse("partner-authentication")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_data = {
            "email": ["This field is required."],
            "password": ["This field is required."],
        }
        self.assertEqual(response.data, expected_data)
