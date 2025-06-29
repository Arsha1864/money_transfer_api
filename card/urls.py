from django.urls import path
from .views import CardCreateView
from .views import resend_card_sms
urlpatterns = [
    path('cards/add/', CardCreateView.as_view(), name='add-card'),
    path('resend_card_sms/', resend_card_sms, name='resend_card_sms'),
]