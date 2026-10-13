from decimal import Decimal as D
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Business, User

from .models import AuditLog, BusinessCategory, Customer, LedgerEntry


class ApiTests(TestCase):
    def setUp(self):
        self.biz = Business.objects.create(name="Mama's Store")
        self.owner = User.objects.create_user(
            username="mama", password="x", business=self.biz, role="OWNER")
        self.helper = User.objects.create_user(
            username="juma", password="x", business=self.biz, role="HELPER")
        self.viewer = User.objects.create_user(
            username="vera", password="x", business=self.biz, role="VIEWER")
        self.cat = BusinessCategory.objects.create(
            business=self.biz, name="Cereals", category_type="CEREAL")
        self.customer = Customer.objects.create(category=self.cat, name="John")

        self.rival_biz = Business.objects.create(name="Rival Store")
        self.rival = User.objects.create_user(
            username="rival", password="x", business=self.rival_biz, role="OWNER")
        self.rival_cat = BusinessCategory.objects.create(
            business=self.rival_biz, name="Onions", category_type="ONION")
        self.rival_customer = Customer.objects.create(
            category=self.rival_cat, name="Rival Customer")

    def as_user(self, user):
        client = APIClient()
        client.force_authenticate(user)
        return client

    def debt(self, **overrides):
        data = {"customer": self.customer.pk, "entry_type": "DEBT",
                "quantity_kg": "50", "price_per_kg": "120", "date": "2026-10-01"}
        data.update(overrides)
        return data

    def post_entry(self, user, data, **extra):
        return self.as_user(user).post("/api/entries/", data, format="json", **extra)

    def test_owner_adds_debt_and_balance_updates(self):
        r = self.post_entry(self.owner, self.debt())
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["amount"], "6000.00")
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, D("6000.00"))

    def test_helper_payment_is_audited_and_flagged(self):
        debt = self.post_entry(self.owner, self.debt(quantity_kg="250")).data  # 30,000
        r = self.post_entry(
            self.helper,
            {"customer": self.customer.pk, "entry_type": "PAYMENT",
             "amount": "25000", "parent_entry": debt["id"],
             "payment_method": "MPESA", "date": "2026-10-02"},
            HTTP_X_DEVICE_ID="phone-1", HTTP_USER_AGENT="TestPhone/1.0",
        )
        self.assertEqual(r.status_code, 201)
        log = AuditLog.objects.get(user=self.helper)
        self.assertEqual(log.ip_address, "127.0.0.1")
        self.assertEqual(log.device_id, "phone-1")
        self.assertEqual(log.device_info, "TestPhone/1.0")
        self.assertTrue(log.is_flagged)
        self.assertEqual(log.business, self.biz)

    def test_viewer_can_read_but_not_write(self):
        r = self.post_entry(self.viewer, self.debt())
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.as_user(self.viewer).get("/api/entries/").status_code, 200)

    def test_only_owner_can_delete_entries(self):
        entry = self.post_entry(self.owner, self.debt()).data
        url = f"/api/entries/{entry['id']}/"
        self.assertEqual(self.as_user(self.helper).delete(url).status_code, 403)
        self.assertEqual(self.as_user(self.owner).delete(url).status_code, 204)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, D("0.00"))
        self.assertTrue(AuditLog.objects.filter(action__startswith="Deleted").exists())

    def test_only_owner_sets_credit_limit(self):
        url = f"/api/customers/{self.customer.pk}/"
        r = self.as_user(self.helper).patch(url, {"credit_limit": "99999"}, format="json")
        self.assertEqual(r.status_code, 400)
        r = self.as_user(self.owner).patch(url, {"credit_limit": "99999"}, format="json")
        self.assertEqual(r.status_code, 200)

    def test_business_isolation(self):
        self.post_entry(self.owner, self.debt())
        rival = self.as_user(self.rival)
        self.assertEqual(
            [c["name"] for c in rival.get("/api/customers/").data], ["Rival Customer"])
        self.assertEqual(rival.get(f"/api/customers/{self.customer.pk}/").status_code, 404)
        self.assertEqual(rival.get("/api/entries/").data, [])
        r = self.post_entry(self.rival, self.debt())  # John belongs to Mama
        self.assertEqual(r.status_code, 400)

    def test_duplicate_client_uuid_saved_and_logged_once(self):
        uid = str(uuid4())
        self.post_entry(self.owner, self.debt(client_uuid=uid))
        r = self.post_entry(self.owner, self.debt(client_uuid=uid))
        self.assertEqual(r.status_code, 201)
        self.assertEqual(LedgerEntry.objects.count(), 1)
        self.assertEqual(AuditLog.objects.count(), 1)

    def test_cannot_hijack_another_businesses_uuid(self):
        uid = str(uuid4())
        self.post_entry(self.owner, self.debt(client_uuid=uid))
        r = self.post_entry(
            self.rival, self.debt(customer=self.rival_customer.pk, client_uuid=uid))
        self.assertEqual(r.status_code, 400)

    def test_overpaying_returns_400(self):
        debt = self.post_entry(self.owner, self.debt()).data  # 6,000
        r = self.post_entry(
            self.owner,
            {"customer": self.customer.pk, "entry_type": "PAYMENT",
             "amount": "7000", "parent_entry": debt["id"]},
        )
        self.assertEqual(r.status_code, 400)

    def test_audit_log_is_owner_only(self):
        self.post_entry(self.helper, self.debt())
        self.assertEqual(self.as_user(self.helper).get("/api/audit-logs/").status_code, 403)
        r = self.as_user(self.owner).get("/api/audit-logs/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data["results"]), 1)