from decimal import Decimal

from Demos.win32ts_logoff_disconnected import username
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import AccountCreationForm
from .models import Account, Transfer


# Create your views here.

from django.contrib import messages, auth
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import UserProfile  # Import your UserProfile model

def login_or_signup(request):
    if request.method == 'POST':
        if 'signup_button' in request.POST:  # Sign-up form submitted
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

            # Ensure UserProfile is created if it doesn't already exist
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)

            messages.success(request, "Sign up successful! You can now log in.")
            return redirect('/login/')

        elif 'login_button' in request.POST:  # Login form submitted
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('/deposit/')
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

                # Check if the account balance is greater than 0 before depositing
                if account.balance == 0:
                    messages.error(request, 'Account balance is zero. You cannot deposit into this account.')
                    return redirect('deposit')  # Redirect back if the balance is zero

                # Deposit amount (add it to the balance of the account)
                account.balance += amount
                account.save()

                # Retrieve the user's profile and decrease the balance (assuming UserProfile model exists)
                user_profile = UserProfile.objects.get(user=request.user)
                if user_profile.balance < amount:
                    messages.error(request, 'Insufficient balance in your profile.')
                    return redirect('deposit')

                user_profile.balance -= amount  # Deduct the deposited amount from the profile balance
                user_profile.save()  # Save the updated user profile balance

                messages.success(request, f'${amount} has been deposited into your account and deducted from your profile balance.')

            except Account.DoesNotExist:
                messages.error(request, 'Account not found.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found.')
            except ValueError:
                messages.error(request, 'Invalid amount entered.')
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

        return redirect('deposit')  # Redirect to the deposit page or another page

    return render(request, 'deposit.html', {'accounts': accounts})

@login_required
def withdraw(request):
    # Get the user's accounts
    user_accounts = Account.objects.filter(user=request.user)

    if request.method == 'POST':
        account_id = request.POST.get('sender_account')
        amount = Decimal(request.POST.get('amount'))

        try:
            account = Account.objects.get(id=account_id, user=request.user)  # Get the selected account

            if account.balance < amount:
                messages.error(request, "Insufficient balance in the selected account.")
                return redirect('withdraw')

            # Deduct the amount from the account
            account.balance -= amount
            account.save()

            # Add the amount to the user's profile balance
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.balance += amount  # Add the withdrawn amount to the profile's balance
            user_profile.save()

            messages.success(request, f"Successfully withdrawn {amount} from your account.")
            return redirect('withdraw')  # Redirect after successful withdrawal

        except Account.DoesNotExist:
            messages.error(request, "Invalid account selection.")
            return redirect('withdraw')
        except UserProfile.DoesNotExist:
            messages.error(request, "User profile not found.")
            return redirect('withdraw')

    # If it's a GET request, render the withdraw page with the user's accounts
    return render(request, 'withdraw.html', {'user_accounts': user_accounts})


@login_required
def send_transfer(request):
    if request.method == 'POST':
        sender_account_number = request.POST.get('sender_account_number')
        receiver_account_number = request.POST.get('receiver_account_number')
        amount = request.POST.get('amount')

        try:
            # Convert the amount to Decimal for accuracy
            amount = Decimal(amount)

            # Get the sender and receiver accounts
            sender_account = Account.objects.get(account_number=sender_account_number)
            receiver_account = Account.objects.get(account_number=receiver_account_number)

            # Check if the sender has sufficient balance
            if sender_account.balance < amount:
                messages.error(request, "Insufficient balance in the sender's account.")
                return redirect('send_transfer')

            # Deduct the amount from the sender's account
            sender_account.balance -= amount
            sender_account.save()

            # Add the amount to the receiver's account
            receiver_account.balance += amount
            receiver_account.save()

            # Create a transfer record
            Transfer.objects.create(
                sender=request.user,
                sender_account=sender_account,
                receiver=receiver_account.user,
                receiver_account=receiver_account,
                amount=amount
            )

            messages.success(request, "Transfer successful!")
            return redirect('send_transfer')  # Redirect to a transfer history page

        except Account.DoesNotExist:
            messages.error(request, "Invalid account number(s).")
            return redirect('send_transfer')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('send_transfer')

    return render(request, 'send_transfer.html')

@login_required
def transfer_history_view(request):
    # Fetch the user's transfers (both sent and received)
    transfers_sent = Transfer.objects.filter(sender=request.user)
    transfers_received = Transfer.objects.filter(receiver=request.user)

    transfer_history = list(transfers_sent) + list(transfers_received)

    # Sort the transfers by timestamp (latest first)
    transfer_history.sort(key=lambda x: x.timestamp, reverse=True)

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


@login_required
def view_profile(request):
    # Get the current user
    user = request.user

    # Get user's profile data (if you have a custom UserProfile model)
    # If you don't have a custom UserProfile, you can access the user attributes directly
    username = user.username
    email = user.email
    # Assuming balance is in the UserProfile model
    try:
        balance = user.profile.balance  # If you have a UserProfile model
    except AttributeError:
        balance = "Not available"  # Fallback if balance is not in UserProfile

    return render(request, 'view_profile.html', {
        'username': username,
        'email': email,
        'balance': balance,
    })