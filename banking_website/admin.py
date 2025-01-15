from django.contrib import admin
from django.contrib.auth.models import User

from banking_website.models import Transfer, Account, UserProfile


#admin.site.register(User)
@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('sender', 'sender_account', 'receiver', 'receiver_account', 'amount', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('sender__username', 'receiver__username', 'sender_account__account_number', 'receiver_account__account_number')
    
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number', 'account_type', 'balance')
    search_fields = ('user__username', 'account_number', 'account_type')
    list_filter = ('account_type',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')  # Fields to display in the admin list view
    search_fields = ('user__username', 'user__email')  # Searchable fields
    list_filter = ('balance',)  # Filter options

admin.site.register(UserProfile, UserProfileAdmin)