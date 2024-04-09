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

# @app.route("/dropDB", methods=['GET'])
# def dropDB():
#     books_ref = db.collection('books')
#     books = books_ref.stream()
#     for book in books:
#         book.reference.delete()
#     return "Database dropped"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search_query']
        books = search_books(search_query)
        # Append the document's name to the dictionary
        for book in books:
            book['idMAIN'] = book.id
            
    else:
        books = get_all_books_cursor()
        for book in books:
            book['idMAIN'] = book['id']
    
    totalbooks = len(books)	
        

    return render_template('index.html', books=books, total_books=totalbooks)



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
    books = get_all_books_cursor(current_count)

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


def get_all_books_cursor():
    books_ref = db.collection('books')
    books = books_ref.stream()
    
    books_list = [book.to_dict() for book in books]  # Convert DocumentSnapshot objects to dictionaries
    return books_list

@app.route('/book/<id>')
def book(id):
    # Get the book who has a field called id with the value of id
    book_ref = db.collection('books').where('id', '==', id).limit(1)
    book = book_ref.stream()
    book_data = [book.to_dict() for book in book][0]
    
    
    return render_template('book.html', book=book_data)

@app.route('/load_initial_books', methods=['GET'])
def load_initial_books():
    books = get_all_books_cursor()
    return jsonify(books)  # jsonif

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)