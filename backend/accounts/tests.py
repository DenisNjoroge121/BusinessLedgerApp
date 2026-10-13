from django.test import TestCase
from django.test import TestCase
from rest_framework.test import APIClient

from .models import User
# Create your tests here.

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.post("/api/auth/register/", {
            "username": "mama", "password": "Str0ng!Pass#99",
            "business_name": "Mama's Store",
        })

    def test_register_creates_owner_with_business(self):
        user = User.objects.get(username="mama")
        self.assertEqual(user.role, "OWNER")
        self.assertEqual(user.business.name, "Mama's Store")

    def test_login_success_returns_tokens(self):
        r = self.client.post("/api/auth/login/",
                             {"username": "mama", "password": "Str0ng!Pass#99"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)

    def test_lockout_after_five_failures(self):
        for _ in range(5):
            self.client.post("/api/auth/login/",
                             {"username": "mama", "password": "wrong"})
        r = self.client.post("/api/auth/login/",
                             {"username": "mama", "password": "Str0ng!Pass#99"})
        self.assertEqual(r.status_code, 423)  # locked even with correct password