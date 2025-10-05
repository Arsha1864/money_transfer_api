# backend/app_name/utils/fcm.py
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests
from django.conf import settings
import logging


logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

def get_fcm_access_token():
    creds = service_account.Credentials.from_service_account_file(
        settings.FIREBASE_SERVICE_ACCOUNT_JSON, scopes=SCOPES
    )
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    return creds.token

def send_fcm_notification_to_token(token, title, body, data=None):
    access_token = get_fcm_access_token()
    project_id = settings.FIREBASE_PROJECT_ID
    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

    message = {
        "message": {
            "token": token,
            "notification": {"title": title, "body": body},
            "android": {
                "priority": "HIGH",
                "notification": {
                    "sound": "default",
                    "icon": "ic_notification",  # ✅ drawable dan
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                },
            },
            "data": data or {},
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    resp = requests.post(url, headers=headers, json=message, timeout=10)
    


