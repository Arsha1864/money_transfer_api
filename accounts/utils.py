import firebase_admin
from firebase_admin import messaging, credentials
from django.conf import settings
import os

# initialize faqat bir marta
if not firebase_admin._apps:
    cred = credentials.Certificate(os.path.join(settings.BASE_DIR, "serviceAccountKey.json"))
    firebase_admin.initialize_app(cred)

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