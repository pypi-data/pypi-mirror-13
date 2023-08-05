from django.test import TestCase
import requests
import responses

# lfs imports
from lfs.core.models import Country
from lfs.order.models import Order
from lfs.order.settings import PAID, PAYMENT_FAILED, PAYMENT_FLAGGED, SUBMITTED

from .models import CompropagoTransaction
from .views import compropago_webhook


class CompropagoPaymentTestCase(TestCase):
    """Tests paypal payments
    """
    fixtures = ['lfs_shop.xml']

    def setUp():
        country = Country.objects.get(code="ie")
        shipping_address = Address.objects.create(
            firstname="bill",
            lastname="blah",
            line1="bills house",
            line2="bills street",
            city="bills town",
            state="bills state",
            zip_code="bills zip code",
            country=country
        )
        invoice_address = Address.objects.create(
            firstname="bill",
            lastname="blah",
            line1="bills house",
            line2="bills street",
            city="bills town",
            state="bills state",
            zip_code="bills zip code",
            country=country
        )
        order = Order(
            invoice_address=invoice_address,
            shipping_address=shipping_address,
            uuid=self.uuid
        )
        self.assertEqual(order.state, SUBMITTED)
        order.save()
        #Aca hay que hacer el setup que hago en las pruebas de compropago

    @responses.activate
    def test_successful_order_transaction(self):
        """
        Test a succesful transaction associated with an order after payment
        """
        self.assertEqual(len(CompropagoTransaction.objects.all()), 0)

        #Paga

        post_params = self.IPN_POST_PARAMS
        response = self.client.post(reverse('paypal-ipn'), post_params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        self.assertEqual(len(CompropagoTransaction.objects.all()), 1)
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.flag, False)
        order = Order.objects.all()[0]
        self.assertEqual(order.state, PAID)
