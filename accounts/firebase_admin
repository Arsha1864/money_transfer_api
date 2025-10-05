import firebase_admin
from firebase_admin import credentials

# JSON fayl yo‘li
cred = credentials.Certificate("serviceAccountKey.json")

# Faqat bir marta initialize qilinadi
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)