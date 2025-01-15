from decimal import Decimal

from django.db import models
import random
import string

from django.core.exceptions import ValidationError

from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2000.00'))

    def __str__(self):
        return f'{self.user.username} Profile'


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('savings', 'Savings'),
        ('checking', 'Checking'),
        ('business', 'Business'),
    ]

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # ForeignKey allows multiple accounts per user
    account_number = models.CharField(max_length=12, unique=True)  # Randomly generated account number
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)  # Account type
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Balance field, default 0.00

    def __str__(self):
        return f'{self.user.username} - {self.account_type}'

    # Method to generate random account number
    def generate_account_number(self):
        return ''.join(random.choices(string.digits, k=12))

    def save(self, *args, **kwargs):
        if not self.account_number:  # Generate the account number if it's not set
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)


class Transfer(models.Model):
    sender = models.ForeignKey('auth.User', related_name='transfers_sent', on_delete=models.CASCADE)  # Sender's User instance
    sender_account = models.ForeignKey('Account', related_name='outgoing_transfers',
                                       on_delete=models.CASCADE)  # Sender's chosen account
    receiver = models.ForeignKey('auth.User', related_name='transfers_received',
                                 on_delete=models.CASCADE)  # Receiver's User instance
    receiver_account = models.ForeignKey('Account', related_name='incoming_transfers',
                                         on_delete=models.CASCADE)  # Receiver's chosen account
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount to be transferred
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of the transfer

    def __str__(self):
        return f'Transfer from {self.sender.username} to {self.receiver.username} of {self.amount}'

    def clean(self):
        # Ensure sender and receiver are not the same person
        if self.sender == self.receiver:
            raise ValidationError("Sender and receiver cannot be the same person.")

        # Ensure the sender's account has enough balance
        if self.sender_account.balance < self.amount:
            raise ValidationError("Insufficient funds in sender's account.")

    def save(self, *args, **kwargs):
        # Validate the transfer before saving
        self.clean()

        # Deduct the amount from sender's account
        self.sender_account.balance -= Decimal(self.amount)
        self.sender_account.save()

        # Add the amount to receiver's account
        self.receiver_account.balance += Decimal(self.amount)
        self.receiver_account.save()

        # Save the transfer record
        super().save(*args, **kwargs)