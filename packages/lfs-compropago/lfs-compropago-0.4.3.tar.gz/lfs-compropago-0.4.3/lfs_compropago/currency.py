from datetime import datetime, timedelta
from django.conf import settings
import requests
import suds
from bs4 import BeautifulSoup
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist

from .models import CompropagoCurrencyConversion as Currency

URL_BASE = 'https://openexchangerates.org/api/'


def to_mxn_openx(value):
    """
    Converts some monetary value to MXN.
    /api/latest.json?app_id=YOUR_APP_ID&symbols=GBP,AED,HKD
    """
    if not getattr(settings, 'LFS_COMPROPAGO_CONVERT_FROM_USD', False):
        return value
    try:
        last_currency = Currency.objects.query(
            currency_code = 'USD',
            created_lt = datetime.now() - timedelta(seconds=3600)
        )[0]
    except IndexError:
        data = requests.get(
            '/'.join((URL_BASE)),
            params = {
                'app_id': settings.LFS_COMPROPAGO_OPENXCHANGE_API_KLEY
            }
        ).json()
        last_currency = Currency(currency_code='USD', rate=data['rates']['MXN'])
        last_currency.save()

    return last_currency.rate * Decimal(str(value))

def last_rate_banxico():
    """
    Asks Banxico for the current rate (USD<->MXN)
    Returns a tuple with the rate and the last update date.
    """
    try:
        last_rate = Currency.objects.get(
            currency_code = 'USD',
            created__lt = datetime.now() - timedelta(seconds=3600)
        )
    except ObjectDoesNotExist:
        banxico = suds.client.Client('http://www.banxico.org.mx/DgieWSWeb/DgieWS?WSDL')
        xmlpayload = banxico.service.tiposDeCambioBanxico()
        xmlpayload = xmlpayload.encode('utf-8')
        xml_soup = BeautifulSoup(xmlpayload, 'xml')
        rate = Decimal(xml_soup.find(IDSERIE="SF60653").findChild()['OBS_VALUE'])
        last_rate = Currency(currency_code='USD', rate=rate)
        last_rate.save()
    return (last_rate.rate, last_rate.created)


def to_mxn_banxico(value):
    """
    Asks Banxico for the current rate (USD<->MXN)
    Returns a tuple with the rate and the last update date.
    """
    if not getattr(settings, 'LFS_COMPROPAGO_CONVERT_FROM_USD', False):
        return value
    conversion_rate, _ = last_rate_banxico()
    return conversion_rate * Decimal(str(value))

to_mxn = to_mxn_banxico
