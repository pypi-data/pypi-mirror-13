from django.shortcuts import render
from django.http import HttpResponse
from django.http import QueryDict
from django.conf import settings

from ebs import BuildGatewayToken
from .forms import GatewayTokenForm
from .forms import GatewaySubmitForm

def index(request):
    if request.method == 'GET':
        __channels = [('0', 'Standard')]
        __currencies = [('USD', "USD"), ('INR', "INR")]
        __modes = [('LIVE', 'LIVE'), ('TEST', 'TEST')]
        __payment_modes = [
            ('', 'All'),
            ('1', "Credit Card"),
            ('2', "Debit Card"),
            ('3', "Net Banking"),
            ('4', "Cash Card"),
            ('5', "Credit Card - EMI"),
            ('6', "Credit Card - Reward Point"),
            ('7', "Paypal")
            ]
        __card_brands = [
            ('', 'All'),
            ('1', "VISA"),
            ('2', "Master Card"),
            ('3', "Maestro"),
            ('4', "Diners Club"),
            ('5', "American Express")
        ]

        form = GatewayTokenForm(
            channels=__channels,
            currencies=__currencies,
            modes=__modes,
            payment_modes=__payment_modes,
            card_brands=__card_brands)
    return render(request, 'gateway/index.html', {'form': form})

def prepare_hash(request):
    if request.method == "POST":
        params = request.POST
        filtered_params = {
            "account_id": params.get('account_id'),
            "address": params.get('address'),
            "amount": params.get('amount'),
            "bank_code": params.get('bank_code'),
            "card_brand": params.get('card_brand'),
            "channel": params.get('channel'),
            "city": params.get('city'),
            "country": params.get('country'),
            "currency": params.get('currency'),
            "description": params.get('description'),
            "email": params.get('email'),
            "emi": params.get('emi'),
            "mode": params.get('mode'),
            "name": params.get('name'),
            "page_id": params.get('page_id'),
            "payment_mode": params.get('payment_mode'),
            "payment_option": params.get('payment_option'),
            "phone": params.get('phone'),
            "postal_code": params.get('postal_code'),
            "reference_no": params.get('reference_no'),
            "return_url": params.get('return_url'),
            "ship_address": params.get('ship_address'),
            "ship_city": params.get('ship_city'),
            "ship_country": params.get('ship_country'),
            "ship_name": params.get('ship_name'),
            "ship_phone": params.get('ship_phone'),
            "ship_postal_code": params.get('ship_postal_code'),
            "ship_state": params.get('ship_state'),
            "state": params.get('state')
            }



        secret = settings.SECRET
        submit_url = settings.SUBMIT_URL
        hash_algorithm = settings.HASH_ALGORITHM

        if(secret is not None && submit_url is not None && hash_algorithm is not None )

        token = BuildGatewayToken(filtered_params, secret, submit_url, hash_algorithm)
        form = GatewaySubmitForm(options=filtered_params, secure_hash=token)
        return render(request, 'gateway/prepare_hash.html', {'data': filtered_params, 'token': token, 'form': form })



def callback(request):
    if request.method == "GET":
        import pdb; pdb.set_trace();
        return render(request, 'gateway/callback.html', {"data": dict(zip(request.GET.keys(), request.GET.values()))})
