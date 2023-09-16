import requests
import os
import dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import cv2
from pyzbar.pyzbar import decode
import time
import click
import colorama


colorama.init(autoreset=True)

dotenv.load_dotenv()
api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame 

cred = credentials.Certificate("serviceAccount.json")

app = firebase_admin.initialize_app(cred)
db = firestore.client()

pygame.init()

pygame.mixer.init()
beep_sound = pygame.mixer.Sound("Success.mp3")  

def get_book_info(isbn):
    url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def log_book(isbn, bookinfo):
    if isbn is None or bookinfo is None or bookinfo.get('totalItems', 0) == 0:
        click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.RED} [{colorama.Fore.WHITE}-{colorama.Fore.RED}] Error: Book not found{colorama.Fore.RESET}")
        return
    book_ref = db.collection('books').document(isbn)
    book_snapshot = book_ref.get()

    if book_snapshot.exists:
        click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.RED} [{colorama.Fore.WHITE}-{colorama.Fore.RED}] Error: Book already registered{colorama.Fore.RESET}")
        return
    formatted_data = bookinfo

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
    book_ref.set(flattened_data)
    click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] Book registered: {isbn}{colorama.Fore.RESET}")
    beep_sound.play()
def loading_animation():
    while True:
        for i in range(4):
            yield f"{colorama.Fore.GREEN}{'.' * i}{' ' * (3 - i)}{colorama.Style.RESET_ALL}"
            time.sleep(0.5)

def test_google_books_api(isbn, wait):
    click.echo("Testing Google Books API...")
    if wait:
        loader = loading_animation()
        for _ in range(5):
            click.echo(next(loader), nl=False)
            time.sleep(0.2)
        click.echo()

    book_info = get_book_info(isbn)
    if book_info is not None:
        click.echo(f"{colorama.Fore.GREEN}Google Books API test passed!{colorama.Fore.RESET}")
    else:
        click.echo(f"{colorama.Fore.RED}Google Books API test failed!{colorama.Fore.RESET}")

def test_database_connection(wait):
    click.echo("Testing database connection...")
    if wait:
        loader = loading_animation()
        for _ in range(5):
            click.echo(next(loader), nl=False)
            time.sleep(0.2)
        click.echo()

    try:
        db.collection('test').document('test').set({'test': 'test'})
        click.echo(f"{colorama.Fore.GREEN}Database connection test passed!{colorama.Fore.RESET}")
    except Exception as e:
        click.echo(f"{colorama.Fore.RED}Database connection test failed. Your credentials may be invalid.{colorama.Fore.RESET}")

@click.command()
@click.option('--test-google-api', is_flag=True, help='Run the Google Books API test')
@click.option('--test-database', is_flag=True, help='Run the database connection test')
@click.option('--no-wait', is_flag=True, help='Do not wait the loading animation')
def main(test_google_api, test_database, no_wait):
    if test_google_api:
        test_google_books_api('9780451524935', wait=not no_wait)
    if test_database:
        test_database_connection(wait=not no_wait)

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    camera = True
    while camera:
        success, img = cap.read()
        for barcode in decode(img):
            isbn = barcode.data.decode('utf-8')
            click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] Barcode: {isbn}{colorama.Fore.RESET}")
            log_book(isbn, get_book_info(isbn))
            time.sleep(0.5)

        cv2.imshow('Result', img)
        cv2.waitKey(1)

if __name__ == '__main__':
    main()
