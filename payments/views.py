from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Subscription
from rest_framework import status
from datetime import timedelta
from django.utils import timezone

class SubscriptionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            sub = Subscription.objects.get(user=user)
            return Response({"last_payment": sub.last_payment})
        except Subscription.DoesNotExist:
            return Response({"last_payment": None})

class PaySubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        # TODO: bu yerda to‘lov logikasini yozing (masalan, kartadan 1000 so‘m yechish)

        sub, created = Subscription.objects.get_or_create(user=user)
        sub.last_payment = timezone.now()
        sub.save()
        return Response({"paid_at": sub.last_payment}, status=status.HTTP_200_OK)