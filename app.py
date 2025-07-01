from flask import Flask, render_template, redirect, Response, request

from library import Library
from util import Book
import time



books_filename = "books.json"

sk_cham_lib = Library()

app = Flask(__name__)


# *** Routes ***

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/library/")
def library():
    return render_template("library.html", books=sk_cham_lib.books)
    

# Borrowing and returning

@app.route("/processing/borrowing/", methods =["POST"])
def borrowing():
    try:
        id = int(request.form.get("phys_id"))
        name = request.form.get("name")
        n_days = int(request.form.get("n_days"))

        sk_cham_lib.borrow(phys_id=id, username=name, n_days=n_days)
    except Exception as e:
        print("Borrowing book failed")
        print(e)
    try:
        sk_cham_lib.save_as_json(books_filename)
    except Exception as e:
        print(e)
        print("Saving JSON library failed")

    return redirect("/library/")

@app.route("/processing/returning/", methods =["POST"])
def returning():
    try:
        id = int(request.form.get("phys_id"))
        stars = int(request.form.get("stars"))
        diff = int(request.form.get("diff"))
        comment = request.form.get("comment")
        
        sk_cham_lib.give_back(phys_id=id, stars=stars, difficulty=diff, comment=comment)
    except Exception as e:
        print(e)
        print("Returning book failed")

    try:
        sk_cham_lib.save_as_json(books_filename)
    except Exception as e:
        print(e)
        print("Saving JSON library failed")

    return redirect("/library/")


# Book and Copy info

@app.route("/copy/<phys_id>")
def copy(phys_id):
    try:
        copy = sk_cham_lib.get_physical_book_by_id(int(phys_id))
        return render_template("copy.html", copy=copy)
    except:
        print("Failed to load copy info")
        return redirect("/library/")

@app.route("/book/<book_id>")
def book(book_id):
    try:
        book = sk_cham_lib.get_book_by_id(int(book_id))
        return render_template("book.html", book=book)
    except:
        print("Failed to load book info")
        return redirect("/library/")


# /processing: Adding and removing stuff

@app.route("/processing/add-book/", methods =["POST"])
def add_book():
    try:
        title = request.form.get("title")
        author = request.form.get("author")
        year = int(request.form.get("year"))
        level_start = int(request.form.get("level_start"))
        level_end = int(request.form.get("level_end"))
        description = request.form.get("description")

        sk_cham_lib.add_book(title=title, 
                             author=author, 
                             year=year, 
                             level_start=level_start, 
                             level_end=level_end, 
                             description=description)
    except Exception as e:
        print(e)
        print("Adding book failed")

    try:
        sk_cham_lib.save_as_json(books_filename)
    except Exception as e:
        print(e)
        print("Saving JSON library failed")

    return redirect("/library/")

@app.route("/processing/add-copy/", methods =["POST"])
def add_copy():
    try:
        book_id = int(request.form.get("book_id"))

        sk_cham_lib.add_copy(book_id=book_id)
    except Exception as e: 
        print(e)
        print("Adding copy failed")

    try:
        sk_cham_lib.save_as_json(books_filename)
    except Exception as e:
        print(e)
        print("Saving JSON library failed")

    return redirect("/library/")

@app.route("/processing/remove-book/<book_id>")
def remove_book(book_id):
    try:
        sk_cham_lib.remove_book(book_id=int(book_id))
    except Exception as e:
        print(e)
        print("Removing book failed")

    try:
        sk_cham_lib.save_as_json(books_filename)
    except Exception as e:
        print(e)
        print("Saving JSON library failed")

    return redirect("/library/")

@app.route("/processing/remove-feedback/<book_id>")
def remove_feedback(book_id):
    try:
        sk_cham_lib.get_book_by_id(int(book_id)).remove_all_feedback()
    except Exception as e:
        print(e)
        print("Removing feedbacks failed")

    try:
        sk_cham_lib.save_as_json(books_filename)
    except Exception as e:
        print(e)
        print("Saving JSON library failed")

    return redirect("/library/")

@app.route("/processing/remove-copy/<phys_id>")
def remove_copy(phys_id):
    try:
        sk_cham_lib.remove_copy(phys_id=int(phys_id))
    except Exception as e:
        print(e)
        print("Removing copy failed")

    try:
        sk_cham_lib.save_as_json(books_filename)
    except Exception as e:
        print(e)
        print("Saving JSON library failed")

    return redirect("/library/")

@app.route("/processing/remove-history/<phys_id>")
def remove_history(phys_id):
    try:
        sk_cham_lib.get_physical_book_by_id(int(phys_id)).remove_history()
    except Exception as e:
        print(e)
        print("Removing history failed")

    try:
        sk_cham_lib.save_as_json(books_filename)
    except Exception as e:
        print(e)
        print("Saving JSON library failed")

    return redirect("/library/")


# Debug

@app.route("/raw/")
def raw_data():
    return Response(
        sk_cham_lib.get_json(),
        mimetype='application/json'
    )


if __name__ == '__main__':
    # Load library
    sk_cham_lib.load_from_json(books_filename)

    # Run app
    app.run(debug=True, port=8000) # Use debug=True for debugging