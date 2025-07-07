

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
    path('api/', include('notifications.urls')),
    path('api/', include('transactions.urls')),
    path('api/', include('payments.urls')),
    path('api/', include('card.urls')),
    path('api/bank/', include('bank_api.urls')),
]