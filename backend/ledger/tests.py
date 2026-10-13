from django.test import TestCase
from datetime import date
from decimal import Decimal as D

from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Business, User

from . import services
from .models import BusinessCategory, CerealItemType, Customer, LedgerEntry
# Create your tests here.

class LedgerServiceTests(TestCase):
    def setUp(self):
        self.business = Business.objects.create(name="Mama's Store")
        self.user = User.objects.create_user(
            username="mama", password="x", business=self.business
        )
        self.cat = BusinessCategory.objects.create(
            business=self.business, name="Cereals", category_type="CEREAL"
        )
        self.maize = CerealItemType.objects.create(
            category=self.cat, name="Maize", default_price_per_kg=D("80.00")
        )
        self.customer = Customer.objects.create(category=self.cat, name="John")

    def add(self, entry_type, amount, on=date(2026, 10, 1), **kw):
        return services.add_entry(
            customer=self.customer, created_by=self.user,
            entry_type=entry_type, amount=D(amount), date=on, **kw,
        )

    def balance(self):
        self.customer.refresh_from_db()
        return self.customer.current_balance

    def test_running_balances_and_zero(self):
        debt = self.add("DEBT", "1000.00", date(2026, 10, 1))
        pay = self.add("PAYMENT", "300.00", date(2026, 10, 2), parent_entry=debt)
        disc = self.add("DISCOUNT", "200.00", date(2026, 10, 3), parent_entry=debt)
        self.assertEqual(debt.running_balance, D("1000.00"))
        self.assertEqual(pay.running_balance, D("700.00"))
        self.assertEqual(disc.running_balance, D("500.00"))
        self.assertEqual(self.balance(), D("500.00"))
        self.add("PAYMENT", "500.00", date(2026, 10, 4), parent_entry=debt)
        self.assertEqual(self.balance(), D("0.00"))

    def test_goods_total_is_calculated(self):
        e = services.add_entry(
            customer=self.customer, created_by=self.user, entry_type="DEBT",
            quantity_kg=D("50"), price_per_kg=D("120"), date=date(2026, 10, 1),
        )
        self.assertEqual(e.amount, D("6000.00"))

    def test_cereal_default_price_autofills(self):
        e = services.add_entry(
            customer=self.customer, created_by=self.user, entry_type="DEBT",
            cereal_type=self.maize, quantity_kg=D("10"), date=date(2026, 10, 1),
        )
        self.assertEqual(e.price_per_kg, D("80.00"))
        self.assertEqual(e.amount, D("800.00"))

    def test_cannot_overpay_a_debt(self):
        debt = self.add("DEBT", "1000.00")
        with self.assertRaises(ValidationError):
            self.add("PAYMENT", "1200.00", parent_entry=debt)
        self.assertEqual(self.balance(), D("1000.00"))

    def test_backdated_entry_recalculates_everything(self):
        self.add("DEBT", "1000.00", date(2026, 10, 5))
        self.add("PAYMENT", "400.00", date(2026, 10, 10))
        self.add("DEBT", "500.00", date(2026, 10, 1))  # arrives late
        balances = [
            e.running_balance
            for e in LedgerEntry.objects.filter(customer=self.customer)
        ]
        self.assertEqual(balances, [D("500.00"), D("1500.00"), D("1100.00")])
        self.assertEqual(self.balance(), D("1100.00"))

    def test_same_client_uuid_is_saved_once(self):
        import uuid
        uid = uuid.uuid4()
        self.add("DEBT", "100.00", client_uuid=uid)
        self.add("DEBT", "100.00", client_uuid=uid)
        self.assertEqual(LedgerEntry.objects.count(), 1)
        self.assertEqual(self.balance(), D("100.00"))

    def test_deleting_a_debt_removes_its_children(self):
        debt = self.add("DEBT", "1000.00")
        self.add("PAYMENT", "300.00", parent_entry=debt)
        services.delete_entry(debt)
        self.assertEqual(self.balance(), D("0.00"))
        self.assertEqual(LedgerEntry.objects.filter(is_deleted=False).count(), 0)

    def test_rejects_cereal_type_from_another_category(self):
        other = BusinessCategory.objects.create(
            business=self.business, name="Onions", category_type="ONION"
        )
        beans = CerealItemType.objects.create(category=other, name="Beans")
        with self.assertRaises(ValidationError):
            services.add_entry(
                customer=self.customer, created_by=self.user, entry_type="DEBT",
                cereal_type=beans, quantity_kg=D("5"),
            )