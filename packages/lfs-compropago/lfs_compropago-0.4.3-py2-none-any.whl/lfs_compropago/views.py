import json
from datetime import datetime
from decimal import getcontext

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from dateutil.parser import parse as parse_date

from lfs.core.signals import order_paid as lfs_order_paid_signal
from lfs.order.settings import PAID, PAYMENT_FAILED
from lfs.mail import utils as mail_utils
from lfs.core.utils import get_default_shop

from compropago import CompropagoAPI, CompropagoCharge

from .models import CompropagoTransaction, CompropagoWebHookHit
from .currency import to_mxn_banxico, last_rate_banxico

# @login_required
def transaction_view(request, tx_id):
    txn = get_object_or_404(CompropagoTransaction, pk=tx_id)

    if not txn.payment_type:
        return payment_selector_view(request, txn)

    if not txn.payment_status:
        shop = get_default_shop(request)
        api = CompropagoAPI(api_key = settings.LFS_COMPROPAGO_API_KEY)
        getcontext().prec=6
        c = CompropagoCharge(
            order_id = str(txn.order.number),
            order_price = str(to_mxn_banxico(txn.order.price)),
            order_name = shop.name,
            customer_name = txn.order.user.get_full_name() or txn.order.user.email,
            customer_email = txn.order.user.email,
            payment_type = txn.payment_type
        )
        r = api.charge(c)
        if r['api_version'] == '1.0':
            txn.payment_id = r['payment_id']
            txn.short_payment_id = r['short_payment_id']
            txn.payment_status = r['payment_status']
            txn.creation_date = parse_date(r['creation_date'], ignoretz=True)
            txn.expiration_date = parse_date(r['expiration_date'], ignoretz=True)
            txn.updated_date = datetime.now()
            txn.product_information = json.dumps(r['product_information'])
            txn.payment_instructions = json.dumps(r['payment_instructions'])
        elif r['api_version'] == '1.1':
            txn.payment_id = r['id']
            txn.short_payment_id = r['short_id']
            txn.payment_status = r['status'].upper()
            txn.creation_date = datetime.fromtimestamp(int(r['created']))
            txn.expiration_date = datetime.fromtimestamp(int(r['exp_date']))
            txn.updated_date = datetime.now()
            order_info = r['order_info']
            txn.product_information = json.dumps({
                "product_id": order_info['order_id'],
                "product_name": order_info['order_name'],
                "product_price": order_info['order_price'],
            })
            instr = r['instructions']
            details = instr['details']
            txn.payment_instructions = json.dumps({
                "step_1": instr['step_1'],
                "step_2": instr['step_2'],
                "step_3": instr['step_3'],
                "note_confirmation": instr['note_confirmation'],
                "description": instr['description'],
                "note_expiration_date": instr['note_expiration_date'],
                "details": {
                    "payment_store": details['store'],
                    "payment_amount": details['amount'],
                    "bank_name": details['bank_name'],
                    "bank_account_number": details['bank_account_number']
                },
                "note_extra_comition": instr['note_extra_comition'],
            })
        txn.save()

    if txn.payment_status in ['PENDING', 'charge.pending']:
        template_name ='compropago/payment_instructions.html'
    else:
        template_name ='compropago/transaction_state.html'

    template_vars = {
        'payment_type_name': dict(txn.PAYMENT_TYPE_CHOICES)[txn.payment_type],
        'logo_filename': '%s.png' % txn.payment_type.lower(),
        'transaction': txn,
        'instructions': json.loads(txn.payment_instructions),
        'order': txn.order,
    }
    return render_to_response(
        template_name,
        RequestContext(request, template_vars)
    )


class PaymentSelectorForm(forms.Form):
    payment_location = forms.ChoiceField(
        choices=CompropagoTransaction.PAYMENT_TYPE_CHOICES,
        widget=forms.RadioSelect()
    )

def payment_selector_view(request, txn, template_name='compropago/payment_method.html'):
    if request.method == 'POST':
        form = PaymentSelectorForm(request.POST)
        if form.is_valid():
            txn.payment_type = form.cleaned_data['payment_location']
            txn.save()
            return  redirect(reverse('compropago_transaction_state', args=[txn.pk]))
    else:
        form = PaymentSelectorForm()
    conversion_rate, last_cr_update = last_rate_banxico()
    template_vars = {
        'form': form,
        'locations': CompropagoTransaction.PAYMENT_TYPE_CHOICES,
        'amount_usd': txn.order.price,
        'amount_mxn': to_mxn_banxico(txn.order.price),
        'conversion_rate': conversion_rate,
        'last_cr_update': last_cr_update,
        'today': datetime.now()
    }
    return render_to_response(
        template_name,
        RequestContext(request, template_vars)
    )


@csrf_exempt
@require_POST
def web_hook_view(request):
    hit = CompropagoWebHookHit(
        scheme = request.is_secure() and 'HTTPS' or 'HTTP',
        headers = repr(request.META),
        path = request.path_info,
        body = request.raw_post_data
    )
    hit.save()

    payload = json.loads(request.raw_post_data)
    api_version = payload['api_version']
    if api_version == '1.1':
        payment_id = payload['id']
    else: #assume 1.0
        payment_id = payload['data']['object']['id']

    txn = get_object_or_404(CompropagoTransaction, payment_id=payment_id)
    hit.transaction = txn
    hit.save()
    api = CompropagoAPI(api_key=settings.LFS_COMPROPAGO_API_KEY)
    res = api.verify_charge(payment_id)
    if 'type' in res:
        pay_status = res['type']
        if pay_status == 'charge.success':
            txn.payment_status = pay_status
            txn.verified = True
            txn.save();
            lfs_order_paid_signal.send({'order': txn.order})
            if getattr(settings, 'LFS_SEND_ORDER_MAIL_ON_PAYMENT', False):
                mail_utils.send_order_received_mail(txn.order)
            txn.order.state = PAID
        elif pay_status == 'error':
            txn.payment_status = PAYMENT_FAILED
            txn.order.state = PAYMENT_FAILED
            txn.order.state_changed = datetime.now()
        txn.save()
        txn.order.save()
    return HttpResponse(str(res), content_type="text/plain")
