from datetime import datetime
from django.conf import settings

import requests

from .model import CompropagoCurrencyConversion as Currency

URL_BASE = 'https://openexchangerates.org/api/'

def to_mxn(value):
    """
    Converts some monetary value to MXN.
    /api/latest.json?app_id=YOUR_APP_ID&symbols=GBP,AED,HKD
    """
    if not getattr(settings, 'LFS_COMPROPAGO_CONVERT_FROM_USD', False):
        return value
    try:
        last_currency = Currency.objects.query(
            currency_code = currency_code,
            created_lt = datetime.now() - timedelta(seconds=3600)
        )[0]
    except IndexError:
        data = requests.get(
            '/'.join((URL_BASE, 'charges', payment_id)),
            params = {
                'app_id': settings.LFS_COMPROPAGO_OPENXCHANGE_API_KLEY
            }
        ).json()
        last_currency = Currency(currency_code='USD', rate=data['rates']['MXN'])
        last_currency.save()

    return last_currency.rate * Decimal(str(value))
