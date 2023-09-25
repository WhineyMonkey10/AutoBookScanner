from flask import Flask, render_template, url_for, request, redirect, jsonify
from bson import json_util
from bson import ObjectId
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase (Replace with your Firebase credentials)
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()


@app.route('/', methods=['GET', 'POST'])
def index():
    books = get_all_books()  # Fetch all books
    if request.method == 'POST':
        search_query = request.form['search_query']
        # Filter books on the client side based on the search query
        if search_query:
            search_query_lowercase = search_query.lower()
            books = [book for book in books if
                     search_query_lowercase in book['title_lowercase'].lower() or
                     search_query_lowercase in book['author'].lower()]

    return render_template('index.html', books=books)



@app.route('/search_books', methods=['POST'])
def search_books_ajax():
    search_query = request.form['search_query']
    books = search_books(search_query)
    # Convert books to a list and serialize using json_util
    books_list = list(books)
    serialized_books = json_util.dumps(books_list)
    return serialized_books

@app.route('/load_more_books', methods=['POST'])
def load_more_books():
    # Get the current number of books displayed on the page
    current_count = int(request.form['current_count'])

    # Fetch more books starting from the current count
    books = get_all_books(skip=current_count, limit=20)

    # Convert books to a list and serialize using json_util
    books_list = list(books)
    serialized_books = json_util.dumps(books_list)

    return serialized_books

def search_books(search_query):
    # Convert the search query to lowercase
    search_query_lowercase = search_query.lower()
    print(f"Searching for: {search_query_lowercase}")

    # Perform a case-insensitive search on the title_lowercase field
    books_ref = db.collection('books')\
        .where('title_lowercase', '>=', search_query_lowercase)\
        .where('title_lowercase', '<=', search_query_lowercase + '\uf8ff')\
        .order_by('title_lowercase')\
        .limit(20)

    # Fetch the documents based on the updated query
    books = books_ref.stream()
    
    return books


def get_all_books(skip=0, limit=None):
    books_ref = db.collection('books')
    books = []
    
    if limit:
        query = books_ref.limit(limit).offset(skip)
    else:
        query = books_ref.offset(skip)
    
    for book in query.stream():
        book_data = book.to_dict()
        # Add the document ISBN, which is the document ID in Firestore, to the book data under the key 'ISBNid'
        book_data['ISBNid'] = book.id
        books.append(book_data)
    
    return books

@app.route('/book/<ISBNid>')
def book(ISBNid):
    book_ref = db.collection('books').document(ISBNid)
    book = book_ref.get()
    book_data = book.to_dict()
    return render_template('book.html', book=book_data)

if __name__ == '__main__':
    app.run(debug=True)
