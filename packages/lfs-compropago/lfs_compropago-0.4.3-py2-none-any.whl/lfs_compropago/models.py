from django.db import models

from lfs.order.models import Order


class CompropagoCurrencyConversion(models.Model):
    class Meta:
        db_table = 'lfs_compropago_currency_conversion'
    currency_code = models.CharField(max_length=4)
    rate = models.DecimalField(max_digits=64, decimal_places=3)
    created = models.DateTimeField(auto_now_add=True)


class CompropagoTransaction(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ("OXXO", "Oxxo"),
        ("SEVEN_ELEVEN", "7 Eleven"),
        ("EXTRA", "Extra"),
        ("CHEDRAUI", "Chedraui"),
        ("ELEKTRA", "Elektra"),
        ("COPPEL", "Coppel"),
        ("FARMACIA_BENAVIDES", "Farmacia Benavides"),
        ("FARMACIA_ESQUIVAR", "Farmacia Esquivar"),
    )
    """A transaction with compropago gateway"""
    class Meta:
        db_table = 'lfs_compropago_transaction'
        ordering = ["-creation_date"]

    order = models.ForeignKey(Order, unique=True)
    payment_status = models.CharField(max_length=32, blank=True)
    payment_type = models.CharField(max_length=255, choices=PAYMENT_TYPE_CHOICES, blank=True)
    payment_id = models.CharField(max_length=255, blank=True)
    short_payment_id = models.CharField(max_length=255, blank=True)
    creation_date = models.DateTimeField(null=True)
    expiration_date = models.DateTimeField(null=True)
    updated_date = models.DateTimeField(null=True)
    product_information = models.TextField(blank=True)
    payment_instructions = models.TextField(blank=True)
    verified = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Compropago transaction id %s' % self.short_payment_id


class CompropagoWebHookHit(models.Model):
    """Stores the headers and body of every call made to the compropago Hook."""
    class Meta:
        db_table = 'lfs_compropago_webhook_hit'
        ordering = ["-created"]

    scheme = models.CharField(max_length=8, null=False)
    headers = models.TextField(max_length=4096, null=False)
    path = models.CharField(max_length=4096, null=False)
    body = models.TextField(null=False)
    transaction = models.ForeignKey(CompropagoTransaction, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'Webhook hit on %s' % self.created
