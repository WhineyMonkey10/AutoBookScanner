import requests
import os
import dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import cv2
import colorama
import cv2
from pyzbar.pyzbar import decode


dotenv.load_dotenv()
api_key = os.getenv('GOOGLE_BOOKS_API_KEY')

# Authenticate to Firebase
cred = credentials.Certificate("serviceAccount.json")

app = firebase_admin.initialize_app(cred)
db = firestore.client()

def get_book_info(isbn):
    url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def log_book(isbn, bookinfo):
    if isbn is None or bookinfo is None or bookinfo['totalItems'] == 0:
        print(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.RED} [{colorama.Fore.WHITE}-{colorama.Fore.RED}] Error: Book not found{colorama.Fore.RESET}")
        return
    book_ref = db.collection('books').document(isbn)
    book_snapshot = book_ref.get()
    
    if book_snapshot.exists:
        print(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.RED} [{colorama.Fore.WHITE}-{colorama.Fore.RED}] Error: Book already registered{colorama.Fore.RESET}")
        return
    data = {}
    for item in bookinfo:
        data[item] = bookinfo[item]
    book_ref.set(data)
    print(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] Book registered: {isbn}{colorama.Fore.RESET}")
    



cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)  

camera = True
while camera:
    success, img = cap.read()
    for barcode in decode(img):
        isbn = barcode.data.decode('utf-8')
        print(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] Barcode: {isbn}{colorama.Fore.RESET}")
        log_book(isbn, get_book_info(isbn))
    
        

    cv2.imshow('Result', img)
    cv2.waitKey(1)