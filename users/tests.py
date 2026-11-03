from django.test import TestCase
from users.models import Payment

class FixtureTest(TestCase):
    fixtures = ['payments.json']

    def test_fixture_loaded(self):
        self.assertEqual(Payment.objects.count(), 2)
        payment = Payment.objects.first()
        self.assertIsNotNone(payment.course)
