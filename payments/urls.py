from django.urls import path
from .views import SubscriptionStatusView, PaySubscriptionView

urlpatterns = [
    path('', SubscriptionStatusView.as_view()),
    path('pay/', PaySubscriptionView.as_view()),
]