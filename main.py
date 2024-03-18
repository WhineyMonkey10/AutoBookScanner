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
import warnings
import sys
import InquirerPy
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator, PathValidator, ValidationError, Validator
#from InquirerPy.prompts import confirm, expand, input, list, rawlist
from InquirerPy.separator import Separator
from InquirerPy.utils import color_print
from InquirerPy import inquirer, prompt
import animation
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
#from InquirerPy.prompts import confirm, expand, input, list, rawlist
from InquirerPy.utils import color_print
from InquirerPy import inquirer, prompt
from InquirerPy.validator import NumberValidator, PathValidator, ValidationError, Validator
from InquirerPy import inquirer
from InquirerPy.base import BaseComplexPrompt
#from InquirerPy.base.list import List
from customtkinter import *



colorama.init(autoreset=True)

dotenv.load_dotenv()
api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.filterwarnings("ignore", category=UserWarning, module="pyzbar.decoder.pdf417")

cred = credentials.Certificate("serviceAccount.json")

app = firebase_admin.initialize_app(cred)
db = firestore.client()

import pygame
pygame.init()

pygame.mixer.init()
success_sound = pygame.mixer.Sound("Success.mp3")
error_sound = pygame.mixer.Sound("Error.mp3")
notfound_sound = pygame.mixer.Sound("NotFound.mp3")

def long_loading_animation():
    while True:
        yield '|'
        yield '/'
        yield '-'
        yield '\\'

def get_book_info(isbn):
    url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def system_message(message):
    click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.LIGHTYELLOW_EX}SYSTEM{colorama.Fore.GREEN}] {message}{colorama.Fore.RESET}")

def log_book(isbn, bookinfo, no_sound):
    if isbn is None or bookinfo is None or bookinfo.get('totalItems', 0) == 0:
        click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.RED} [{colorama.Fore.WHITE}-{colorama.Fore.RED}] Error: Book not found{colorama.Fore.RESET}")
        if not no_sound:
            notfound_sound.play()
        return
    book_ref = db.collection('books').document(isbn)
    book_snapshot = book_ref.get()

    if book_snapshot.exists:
        click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.RED} [{colorama.Fore.WHITE}-{colorama.Fore.RED}] Error: Book already registered{colorama.Fore.RESET}")
        if not no_sound:
            error_sound.play()
        return
    formatted_data = bookinfo
    if not no_sound:
        success_sound.play()

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

    flattened_data = {key.replace('items_', '').replace('0_', ''): value for key, value in flattened_data.items()}
    book_ref.set(flattened_data)
    click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] Book registered: {isbn}{colorama.Fore.RESET}")

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
        system_message("Google Books API test passed!")
    else:
        system_message("Google Books API test failed. Your credentials may be invalid.")

def test_database_connection(wait):
    system_message("Testing database connection...")
    if wait:
        loader = loading_animation()
        for _ in range(5):
            click.echo(next(loader), nl=False)
            time.sleep(0.2)
        click.echo()

    try:
        db.collection('test').document('test').set({'test': 'test'})
        system_message("Database connection test passed!")
    except Exception as e:
        system_message("Database connection test failed. Your credentials may be invalid.")


@click.command()
@click.option('--test-google-api', is_flag=True, help=f'{colorama.Fore.MAGENTA}Run the Google Books API test{colorama.Fore.RESET}')
@click.option('--test-database', is_flag=True, help=f'{colorama.Fore.MAGENTA}Run the database connection test{colorama.Fore.RESET}')
@click.option('--no-wait', is_flag=True, help=f'{colorama.Fore.MAGENTA}Do not unnecessarily wait.{colorama.Fore.RESET}')
@click.option('--book-isbn', help=f'{colorama.Fore.MAGENTA}Log a book with the specified ISBN{colorama.Fore.RESET}')
@click.option('--manual', is_flag=True, help=f'{colorama.Fore.MAGENTA}Manually enter the book data, however, only a limited amount of data can be entered{colorama.Fore.RESET}')
@click.option('--print-book-list', is_flag=True, help=f'{colorama.Fore.MAGENTA}Debug the book list{colorama.Fore.RESET}')
@click.option('--timeout', default=0.5, help=f'{colorama.Fore.MAGENTA}Set the timeout for the interval between each barcode scan (s) (default: 0.5){colorama.Fore.RESET}')
@click.option('--log-isbn', is_flag=True, help=f'{colorama.Fore.MAGENTA}Instead of processing the barcode, all scanned ISBNs will be logged to isbn-log.txt{colorama.Fore.RESET}')
@click.option('--process-log', is_flag=True, help=f'{colorama.Fore.MAGENTA}Process the ISBNs in isbn-log.txt{colorama.Fore.RESET}') 
@click.option('--no-sound', is_flag=True, help=f'{colorama.Fore.MAGENTA}Disable sound effects{colorama.Fore.RESET}')
@click.option('--web-server', is_flag=True, help=f'{colorama.Fore.MAGENTA}Run the web server{colorama.Fore.RESET}')
@click.option('--version-switch', is_flag=True, help=f'{colorama.Fore.MAGENTA}Switch to Python 3 (default: Python 2){colorama.Fore.RESET}')
@click.option('--recommended-flags', is_flag=True, help=f'{colorama.Fore.MAGENTA}Run the recommended flags{colorama.Fore.RESET}')
def main(test_google_api, test_database, no_wait, book_isbn, print_book_list, timeout, manual, log_isbn, process_log, no_sound, web_server, version_switch, recommended_flags):
    if recommended_flags:
        system_message("Running recommended flags...")
        test_google_api = True
        test_database = True
        timeout = 1
        system_message(f"Recommended flags set. Test Google Books API: {test_google_api}, Test database connection: {test_database}, Timeout: {timeout}")
        no_sound = False
        no_wait = False
    if test_google_api:
        test_google_books_api('9780451524935', wait=not no_wait)
    if test_database:
        test_database_connection(wait=not no_wait)

    if manual:
        ISBN = input(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] ISBN: {colorama.Fore.RESET}")
        if ISBN is None or get_book_info(ISBN) is None or log_book(ISBN, get_book_info(ISBN), no_sound)["totalItems"] == 0:
            click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.RED} [{colorama.Fore.WHITE}-{colorama.Fore.RED}] Error: Book not found{colorama.Fore.RESET}")
            return
        else:
            click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] Book registered: {ISBN}{colorama.Fore.RESET}")
            return 0
    if log_isbn:
        system_message("Logging ISBNs to isbn-log.txt")
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 720)

        camera = True
        while camera:
            success, img = cap.read()
            for barcode in decode(img):
                isbn = barcode.data.decode('utf-8')
                click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] Barcode: {isbn}{colorama.Fore.RESET}")
                if isbn is not None and isbn not in open('isbn-log.txt', 'r').read():
                    click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] Logging ISBN: {isbn}{colorama.Fore.RESET}")
                    with open('isbn-log.txt', 'a') as f:
                        f.write(isbn + '\n')
                    time.sleep(timeout)

                    cv2.imshow('Result', img)
                    cv2.waitKey(1)
                else:
                    click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.RED} [{colorama.Fore.WHITE}-{colorama.Fore.RED}] Error: Barcode already logged{colorama.Fore.RESET}")
    if process_log:
        if not os.path.isfile('isbn-log.txt'):
            click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.RED} [{colorama.Fore.WHITE}-{colorama.Fore.RED}] Error: isbn-log.txt does not exist, use --log-isbn to create it{colorama.Fore.RESET}")
            return
        if os.stat('isbn-log.txt').st_size == 0:
            click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.RED} [{colorama.Fore.WHITE}-{colorama.Fore.RED}] Error: isbn-log.txt is empty{colorama.Fore.RESET}")
            return
        with open('isbn-log.txt', 'r') as f:
            lines = f.readlines()

        processed_isbns = []  # To keep track of successfully processed ISBNs

        for isbn in open('isbn-log.txt', 'r').read().split('\n'):
            if isbn != '':
                data = log_book(isbn, get_book_info(isbn), no_sound)
                if isbn is None or data is None or data.get('totalItems', 0) == 0:
                    if data is not None:
                        click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.RED} [{colorama.Fore.WHITE}-{colorama.Fore.RED}] Error: Book not found for ISBN: {isbn}{colorama.Fore.RESET}")
                else:
                    processed_isbns.append(isbn)  # Add to the list of successfully processed ISBNs

        # Remove processed (registered) ISBNs from 'isbn-log.txt' at the end
        with open('isbn-log.txt', 'w') as f:
            for line in lines:
                isbn = line.strip('\n')
                if isbn not in processed_isbns:
                    f.write(line)

        click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] All ISBNs processed. Found books have been registered and removed from the file.{colorama.Fore.RESET}")
        return 0


    if book_isbn:
        log_book(book_isbn, get_book_info(book_isbn), no_sound)
        return 0
    if print_book_list:
        click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] Print book list{colorama.Fore.RESET}")
        books = db.collection('books').get()
        book_amount = len(books)
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
                                items.update(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep))
                            else:
                                items[f"{new_key}{sep}{i}"] = item
                    else:
                        items[new_key] = v
                return items


            flattened_data = flatten_dict(formatted_data)
            flattened_data = {key.replace('items_', '').replace('0_', ''): value for key, value in flattened_data.items()}
            print(flattened_data)
            print('\n' + '-'*40 + '\n')
            
        print(f"Total books: {book_amount}")
        return 0
    if web_server:
        system_message("Starting web server using PYTHON, not PYTHON 3. If you'd like to use PYTHON 3, use the --version-switch flag.")
        if version_switch:
            click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] Switching to PYTHON 3...{colorama.Fore.RESET}")
            os.system('python3 web_server.py')
            return 0
        else:
            os.system('python web_server.py')
            return 0

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    system_message("Starting barcode scanner...")
    system_message(f"Timeout: {timeout}s")
    system_message("Barcode scanner started.")
    camera = True
    while camera:
        success, img = cap.read()
        if not success:
            continue  # Skip frames with no data
        
        barcodes = decode(img)
        if barcodes:
            for barcode in barcodes:
                isbn = barcode.data.decode('utf-8')
                click.echo(f"{colorama.Fore.MAGENTA}>>{colorama.Fore.GREEN} [{colorama.Fore.WHITE}+{colorama.Fore.GREEN}] Barcode: {isbn}{colorama.Fore.RESET}")
                log_book(isbn, get_book_info(isbn), no_sound)
                time.sleep(timeout)

        cv2.imshow('Result', img)
        cv2.waitKey(1)

if __name__ == '__main__':
    main()



# TODOD: Fix the bug where already registered or newly registered books are not being deleted from the log file (process-log option)