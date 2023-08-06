from django import forms

class GatewayTokenForm(forms.Form):
    channel = forms.ChoiceField(widget=forms.Select(),
                                required=True
                                )
    account_id = forms.IntegerField()
    reference_no = forms.IntegerField()
    amount = forms.FloatField()
    currency = forms.ChoiceField(widget=forms.Select(),
                                required=True)
    description = forms.CharField(label='Description')
    return_url = forms.URLField(label='Return Url', required=True)
    return_url = forms.URLField(label='Return Url', required=True)
    mode = forms.ChoiceField(widget=forms.Select(),
                                required=True)
    payment_mode = forms.ChoiceField(widget=forms.Select(),
                                required=True)
    payment_option = forms.ChoiceField(widget=forms.Select(),
                                required=True)
    card_brand = forms.ChoiceField(widget=forms.Select(),
                                required=True)
    bank_code = forms.CharField(label='Bank Code')
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    emi = forms.FloatField(label="emi", widget=forms.TextInput(attrs={'placeholder': 'emi'}))
    page_id = forms.IntegerField(label="Page Id", widget=forms.TextInput(attrs={'placeholder': 'Page id'}))
    name = forms.CharField(label="Name", widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    address = forms.CharField(label="Address", widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    city = forms.CharField(label="City", widget=forms.TextInput(attrs={'placeholder': 'City'}))
    state = forms.CharField(label="State", widget=forms.TextInput(attrs={'placeholder': 'State'}))
    postal_code = forms.CharField(label="Postal Code", widget=forms.TextInput(attrs={'placeholder': 'Postal Code'}))
    country = forms.CharField()
    phone = forms.CharField()

    ship_name = forms.CharField(label="Ship Name")
    ship_address = forms.CharField(label="Ship Address")
    ship_city = forms.CharField(label="Ship City")
    ship_state = forms.CharField(label="Ship State", widget=forms.TextInput(attrs={'placeholder': 'Ship State'}))
    ship_postal_code = forms.CharField(label="Postal Code", widget=forms.TextInput(attrs={'placeholder': 'Ship Postal Code'}))
    ship_country = forms.CharField()
    ship_phone = forms.CharField()

    def __init__(self, *args, **kwargs):
        channels = kwargs.pop('channels')
        currencies = kwargs.pop('currencies')
        modes = kwargs.pop('modes')
        payment_modes = kwargs.pop('payment_modes')
        card_brands = kwargs.pop('card_brands')

        super(GatewayTokenForm, self).__init__(*args, **kwargs)


        self.fields['channel'].choices = channels
        self.fields['currency'].choices = currencies
        self.fields['mode'].choices = modes
        self.fields['payment_mode'].choices = payment_modes
        self.fields['card_brand'].choices = card_brands



class GatewaySubmitForm(forms.Form):
    account_id = forms.IntegerField(widget=forms.HiddenInput())
    address = forms.CharField(widget=forms.HiddenInput())
    amount = forms.FloatField(widget=forms.HiddenInput())
    bank_code = forms.CharField(widget=forms.HiddenInput())
    card_brand = forms.ChoiceField(widget=forms.HiddenInput())
    channel = forms.ChoiceField(widget=forms.HiddenInput())
    city = forms.CharField(widget=forms.HiddenInput())
    country = forms.CharField(widget=forms.HiddenInput())
    currency = forms.ChoiceField(widget=forms.HiddenInput())
    description = forms.CharField(widget=forms.HiddenInput())
    email = forms.EmailField(widget=forms.HiddenInput())
    emi = forms.FloatField(widget=forms.HiddenInput())
    mode = forms.ChoiceField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.HiddenInput())
    page_id = forms.IntegerField(widget=forms.HiddenInput())
    payment_mode = forms.ChoiceField(widget=forms.HiddenInput())
    payment_option = forms.ChoiceField(widget=forms.HiddenInput())
    phone = forms.CharField(widget=forms.HiddenInput())
    postal_code = forms.CharField(widget=forms.HiddenInput())
    reference_no = forms.IntegerField(widget=forms.HiddenInput())
    return_url = forms.URLField(widget=forms.HiddenInput())
    ship_address = forms.CharField(widget=forms.HiddenInput())
    ship_city = forms.CharField(widget=forms.HiddenInput())
    ship_country = forms.CharField(widget=forms.HiddenInput())
    ship_name = forms.CharField(widget=forms.HiddenInput())
    ship_phone = forms.CharField(widget=forms.HiddenInput())
    ship_postal_code = forms.CharField(widget=forms.HiddenInput())
    ship_state = forms.CharField(widget=forms.HiddenInput())
    state = forms.CharField(widget=forms.HiddenInput())
    secure_hash = forms.CharField(widget=forms.HiddenInput())



    def __init__(self, *args, **kwargs):
        options = kwargs.pop('options')
        secure_hash = kwargs.pop('secure_hash')
        super(GatewaySubmitForm, self).__init__(*args, **kwargs)
        # import pdb; pdb.set_trace();
        self.fields['channel'].initial = options['channel']
        self.fields['account_id'].initial = options['account_id']
        self.fields['reference_no'].initial = options['reference_no']
        self.fields['currency'].initial = options['currency']
        self.fields['description'].initial = options['description']
        self.fields['return_url'].initial = options['return_url']
        self.fields['amount'].initial = options['amount']
        self.fields['mode'].initial = options['mode']
        self.fields['payment_mode'].initial = options['payment_mode']
        self.fields['card_brand'].initial = options['card_brand']
        self.fields['bank_code'].initial = options['bank_code']
        self.fields['email'].initial = options['email']
        self.fields['emi'].initial = options['emi']
        self.fields['page_id'].initial = options['page_id']
        self.fields['name'].initial = options['name']
        self.fields['address'].initial = options['address']

        self.fields['city'].initial = options['city']
        self.fields['state'].initial = options['state']
        self.fields['postal_code'].initial = options['postal_code']
        self.fields['country'].initial = options['country']
        self.fields['phone'].initial = options['phone']

        self.fields['ship_name'].initial = options['ship_name']
        self.fields['ship_address'].initial = options['ship_address']
        self.fields['ship_city'].initial = options['ship_city']
        self.fields['ship_state'].initial = options['ship_state']
        self.fields['ship_postal_code'].initial = options['ship_postal_code']
        self.fields['ship_country'].initial = options['ship_country']
        self.fields['ship_phone'].initial = options['ship_phone']
        self.fields['secure_hash'].initial = secure_hash
