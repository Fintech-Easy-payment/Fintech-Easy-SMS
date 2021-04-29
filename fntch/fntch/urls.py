
from django.contrib import admin
from django.urls import path
from user import api as user_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/payment-info/', user_api.get_payment_info),
]
