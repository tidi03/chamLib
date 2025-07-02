from flask import Flask, render_template, redirect, Response, request, session, url_for

from library import Library
import os
import json


books_filename = "books.json"

sk_cham_lib = Library()
sk_cham_lib.load_from_json(books_filename)

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Load users and admin password from environment variables
users = {}
raw = os.environ.get("USERS_JSON", '{"Alice":"password123"}')
try:
    users = json.loads(raw)
except json.JSONDecodeError:
    users = {}

users['admin'] = os.environ.get("ADMIN_PASSWORD", "admin")

# *** Routes ***

@app.route("/")
def library():
    books = sk_cham_lib.books
    username = session.get('username', 'anonymous')
    return render_template("library.html", books=books, username=username)


# Login
@app.route("/login/", methods=["GET", "POST"])
def login():
    if 'username' in session:
        print("User already logged in")
        return redirect(url_for("library"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for("library"))
        else:
            return render_template("login.html", failed=True)
    return render_template("login.html", failed=False)

@app.route("/logout/")
def logout():
    session.pop('username', None)
    return redirect(url_for("library"))


# Borrowing and returning

@app.route("/processing/borrowing/", methods =["POST"])
def borrowing():
    if 'username' not in session:
        print("User not logged in")
        return redirect(url_for("login"))

    try:
        id = int(request.form.get("phys_id"))
        n_days = int(request.form.get("n_days"))
        username = session.get('username')

        sk_cham_lib.borrow(phys_id=id, n_days=n_days, username=username)
    except Exception as e:
        print("Borrowing book failed")
        print(e)
        return render_template("borrowed_or_returned.html", action="error")

    try:
        sk_cham_lib.save_as_json(books_filename)
    except Exception as e:
        print(e)
        print("Saving JSON library failed")

    return render_template("borrowed_or_returned.html", action="borrowed")

@app.route("/processing/returning/", methods =["POST"])
def returning():
    if 'username' not in session:
        print("User not logged in")
        return redirect(url_for("login"))

    try:
        id = int(request.form.get("phys_id"))
        stars = int(request.form.get("stars"))
        diff = int(request.form.get("diff"))
        comment = request.form.get("comment")
        
        sk_cham_lib.give_back(phys_id=id, stars=stars, difficulty=diff, comment=comment)
    except Exception as e:
        print(e)
        print("Returning book failed")
        return render_template("borrowed_or_returned.html", action="error")

    try:
        sk_cham_lib.save_as_json(books_filename)
    except Exception as e:
        print(e)
        print("Saving JSON library failed")

    return render_template("borrowed_or_returned.html", action="returned")


# Book and Copy info

@app.route("/copy/<phys_id>")
def copy_view(phys_id):
    try:
        copy = sk_cham_lib.get_physical_book_by_id(int(phys_id))
        print(copy)
        username = session.get('username', 'anonymous')
        return render_template("copy.html", copy=copy, username=username)
    except:
        print("Failed to load copy info")
        return redirect("/")
    
@app.route("/book/<book_id>")
def book_view(book_id):
    try:
        book = sk_cham_lib.get_book_by_id(int(book_id))
        print(book)
        username=session.get('username', 'anonymous')
        return render_template("book.html", book=book, username=username)
    except:
        print("Failed to load book info")
        return redirect("/")


# /processing: Adding and removing stuff

@app.route("/processing/add-book/", methods =["POST"])
def add_book():
    if session.get('username') != 'admin':
        return "Unauthorized", 403

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

    return redirect("/")

@app.route("/processing/add-copy/", methods =["POST"])
def add_copy():
    if session.get('username') != 'admin':
        return "Unauthorized", 403

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

    return redirect("/")

@app.route("/processing/remove-book/<book_id>")
def remove_book(book_id):
    if session.get('username') != 'admin':
        return "Unauthorized", 403

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

    return redirect("/")

@app.route("/processing/remove-feedback/<book_id>")
def remove_feedback(book_id):
    if session.get('username') != 'admin':
        return "Unauthorized", 403

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

    return redirect("/")

@app.route("/processing/remove-copy/<phys_id>")
def remove_copy(phys_id):
    if session.get('username') != 'admin':
        return "Unauthorized", 403

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

    return redirect("/")

@app.route("/processing/remove-history/<phys_id>")
def remove_history(phys_id):
    if session.get('username') != 'admin':
        return "Unauthorized", 403

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

    return redirect("/")


# Debug

@app.route("/raw/")
def raw_data():
    return Response(
        sk_cham_lib.get_json(),
        mimetype='application/json'
    )


if __name__ == "__main__":
    app.run(debug=True, port=8000) # Use for debugging