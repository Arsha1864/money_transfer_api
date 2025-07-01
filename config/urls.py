

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def home(request):
    return HttpResponse("Bosh sahifa ishlayapti!")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path("", home, name='home'),  # Asosiy URL uchun funksiya
    path('api/notifications/', include('notifications.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/card/', include('card.urls')),
]