from flask import Flask, render_template, url_for
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase (Replace with your Firebase credentials)
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

books = [
    {
        "id": "gsR7zwEACAAJ",
        "thumbnail_url": "http://books.google.com/books/content?id=gsR7zwEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api",
        "title": "The Door of No Return",
        "author": "Kwame Alexander",
        "published_date": "2023-03-02",
        "rating": 5,
        "isbn": "9781839133244",
    },
    # Add more book data as needed
]

@app.route("/")
def book_list():
    return render_template("index.html", books=books)

if __name__ == "__main__":
    app.run(debug=True)