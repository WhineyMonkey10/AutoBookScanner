from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin
import cv2
import colorama
import cv2
from pyzbar.pyzbar import decode
import time



# Authenticate to Firebase
cred = credentials.Certificate("serviceAccount.json")

app = firebase_admin.initialize_app(cred)
db = firestore.client()

books = db.collection('books').get()
for book in books:
    print(book.to_dict())
    
    print('''
    
    
    
    
    ''')
