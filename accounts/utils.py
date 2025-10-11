import firebase_admin
from firebase_admin import messaging, credentials
from django.conf import settings
import os, json

# Firebase init
if not firebase_admin._apps:
    try:
        if os.path.exists(os.path.join(settings.BASE_DIR, "serviceAccountKey.json")):
            cred = credentials.Certificate(os.path.join(settings.BASE_DIR, "serviceAccountKey.json"))
        else:
            firebase_json = os.getenv("FIREBASE_CONFIG")
            if firebase_json:
                cred = credentials.Certificate(json.loads(firebase_json))
            else:
                raise ValueError("❌ FIREBASE_CONFIG environment variable not found")

        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized successfully")
    except Exception as e:
        print("❌ Firebase initialization failed:", e)

def send_push_notification(token, title, body, image=None):
    try:
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image if image else None,
        )

        message = messaging.Message(
            notification=notification,
            token=token,
        )

        response = messaging.send(message)
        print("✅ Firebase message ID:", response)
        return True
    except Exception as e:
        print("❌ Firebase error:", e)
        return False