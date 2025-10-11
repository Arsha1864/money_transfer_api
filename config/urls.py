

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    return HttpResponse("Bosh sahifa ishlayapti!")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path("", home, name='home'),  # Asosiy URL uchun funksiya
    path('api/', include('transactions.urls')),
    path('api/', include('payments.urls')),
    path('api/', include('card.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

