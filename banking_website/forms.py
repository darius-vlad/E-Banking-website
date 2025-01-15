from django import forms
from .models import Account, Transfer


class AccountCreationForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['account_type']  # Only account type, because account number is auto-generated

    account_type = forms.ChoiceField(choices=Account.ACCOUNT_TYPE_CHOICES, widget=forms.RadioSelect)

    # Additional validation or customization can be added here if needed


class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['sender_account', 'receiver', 'receiver_account', 'amount']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Pass the logged-in user to filter sender accounts
        super().__init__(*args, **kwargs)
        self.fields['sender_account'].queryset = Account.objects.filter(user=user)