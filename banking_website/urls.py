"""
URL configuration for ebanking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from banking_website import views
from banking_website.views import  login_or_signup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_or_signup, name='login_or_signup'),
    path('deposit/', views.deposit_view, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('send_transfer/', views.send_transfer, name='send_transfer'),
    path('transfer_history/', views.transfer_history_view, name='transfer_history'),
    path('create_account/', views.create_account_view, name='create_account'),
    path('account_history/', views.account_history_view, name='account_history'),
    path('view-profile/', views.view_profile, name='view_profile')
]
