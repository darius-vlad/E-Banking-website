from django import forms
from .models import Account


class AccountCreationForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['account_type']  # Only account type, because account number is auto-generated

    account_type = forms.ChoiceField(choices=Account.ACCOUNT_TYPE_CHOICES, widget=forms.RadioSelect)

    # Additional validation or customization can be added here if needed
