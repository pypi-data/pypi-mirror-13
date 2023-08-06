# django imports
from django.core.urlresolvers import reverse

# lfs imports
from lfs.plugins import PaymentMethodProcessor
from lfs.plugins import PM_ORDER_IMMEDIATELY

class CompropagoMethodProcessor(PaymentMethodProcessor):
    def process(self):
        from .models import CompropagoTransaction
        tx = CompropagoTransaction(
            order = self.order
        )
        tx.save()
        return {
            "accepted": True,
            "next_url": reverse('compropago_transaction_state', args=[tx.pk])
        }

    def get_create_order_time(self):
        return PM_ORDER_IMMEDIATELY

    def get_pay_link(self):
        txn = self.order.compropagotransaction_set.get()
        return reverse('compropago_transaction_state', args=[txn.pk])
