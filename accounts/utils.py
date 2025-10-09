from firebase_admin import messaging

def send_push_notification(token, title, body, image=None):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image if image else None
            ),
            token=token,
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    sound="default",
                    click_action="FLUTTER_NOTIFICATION_CLICK",
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                        content_available=True,
                    )
                )
            ),
            data={
                "click_action": "FLUTTER_NOTIFICATION_CLICK",
                "screen": "notifications_page",
            },
        )
        response = messaging.send(message)
        print(f"✅ Notification sent successfully: {response}")
        return True
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False

