import firebase_admin
from firebase_admin import credentials, messaging
import os

from config.settings import BASE_DIR

# Fayl joylashgan manzil (loyihangda joylashgan joyga qarab o‘zgartir)
cred = credentials.Certificate(
    os.path.join(BASE_DIR, "serviceAccountKey.json")
)

# Firebase ilovasini bir marta initialize qilamiz
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)