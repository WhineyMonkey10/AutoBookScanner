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
    formatted_data = book.to_dict()

    # Function to flatten a nested dictionary
    def flatten_dict(d, parent_key='', sep='_'):
        items = {}
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.update(flatten_dict(v, new_key, sep=sep))
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.update(flatten_dict(item, new_key, sep=sep))
                    else:
                        items[f"{new_key}_{i}"] = item
            else:
                items[new_key] = v
        return items

    flattened_data = flatten_dict(formatted_data)

    # Remove 'items_' prefix and '0_' prefix from the keys
    flattened_data = {key.replace('items_', '').replace('0_', ''): value for key, value in flattened_data.items()}

    print(flattened_data)

    print('\n' + '-'*40 + '\n')  # Add a separator between records