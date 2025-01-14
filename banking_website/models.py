from django.db import models
import random
import string

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

