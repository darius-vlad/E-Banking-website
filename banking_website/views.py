from decimal import Decimal

from Demos.win32ts_logoff_disconnected import username
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import AccountCreationForm
from .models import Account
# Create your views here.

def login_or_signup(request):
    if request.method == 'POST':
        # Check which form was submitted
        if 'signup_button' in request.POST:  # If the sign-up button was clicked
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect('/login/')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken.")
                return redirect('/login/')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already taken.")
                return redirect('/login/')

            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Sign up successful! You can now log in.")
            return redirect('/login/')

        elif 'login_button' in request.POST:  # If the login button was clicked
            username = request.POST['username']  # Use username field
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)  # Authenticate using username

            if user is not None:
                login(request, user)  # Log the user in
                messages.success(request, "Login successful!")
                return redirect('/deposit/')  # Redirect to the deposit page
            else:
                messages.error(request, "Invalid username or password.")
                return redirect('/login/')

    return render(request, 'login.html')

@login_required
def deposit_view(request):
    # Get the logged-in user's accounts
    accounts = Account.objects.filter(user=request.user)

    if request.method == 'POST':
        account_id = request.POST.get('account')
        amount = request.POST.get('amount')

        # Check if the account and amount are valid
        if account_id and amount:
            try:
                amount = Decimal(amount)  # Convert amount to Decimal

                # Check if the amount is positive
                if amount <= 0:
                    messages.error(request, 'Amount must be greater than zero.')
                    return redirect('deposit')  # Redirect back if the amount is invalid

                # Retrieve the selected account
                account = Account.objects.get(id=account_id, user=request.user)

                # Deposit amount (add it to the balance)
                account.balance += amount
                account.save()

                messages.success(request, f'${amount} has been deposited into your account.')

            except Account.DoesNotExist:
                messages.error(request, 'Account not found.')
            except ValueError:
                messages.error(request, 'Invalid amount entered.')
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

        return redirect('deposit')  # Redirect to the deposit page or another page

    return render(request, 'deposit.html', {'accounts': accounts})
@login_required
def withdraw_view(request):
    return render(request, 'withdraw.html')

@login_required
def send_transfer_view(request):
    return render(request, 'send_transfer.html')

@login_required
def transfer_history_view(request):
    # Fetch the user's transfer history (this is just a placeholder)
    # In a real application, you would query the database for the user's transfers
    transfer_history = [
        {'sender': 'John Doe', 'receiver': 'Jane Smith', 'amount': 500, 'date': '01 Dec, 2023', 'status': 'Completed'},
        {'sender': 'Mary Johnson', 'receiver': request.user.username, 'amount': 1200, 'date': '30 Nov, 2023',
         'status': 'Failed'},
        {'sender': 'Michael Brown', 'receiver': 'Chris White', 'amount': 350, 'date': '29 Nov, 2023',
         'status': 'Pending'}
    ]

    return render(request, 'transfer_history.html', {'transfer_history': transfer_history})


@login_required
def create_account_view(request):
    if request.method == 'POST':
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user  # Associate the account with the logged-in user
            account.save()  # Save the account to the database
            return redirect('account_history')  # Redirect to a success page (you can create this view)
    else:
        form = AccountCreationForm()

    return render(request, 'create_account.html', {'form': form})


@login_required
def account_history_view(request):
    accounts = Account.objects.filter(user=request.user)  # Get all accounts for the logged-in user
    return render(request, 'account_history.html', {'accounts': accounts})