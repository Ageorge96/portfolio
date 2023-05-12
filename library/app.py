import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

# configure Flask
app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# connect application to media database
con = sqlite3.connect("media.db", check_same_thread=False)

# create cursor to allow sql statments and queries
cur = con.cursor()

# homepage
@app.route("/")
def index():
    return render_template("index.html")

# library page will store owned books
@app.route("/library", methods=["GET"])
def library():

    if request.method == "GET":

        # collect list of books from the SQL library database
        library = cur.execute("SELECT * FROM library").fetchall()

        # initialise an empty list to store books
        books = []

        # for each book in the library list
        for book in library:

            # add each book as a dictionary containing the book's information to the books list

            books.append({
                "title": book[0],
                "author": book[1],
                "series": book[2],
                "genre": book[3],
                "pages": book[4],
                "status": book[5],
                "bookmark": book[6]
            })

        return render_template("library.html", books=books)


@app.route("/library/add", methods=["POST"])
def add_to_library():

    if request.method == "POST":

        # get user inputs
        title = request.form.get("title")
        author = request.form.get("author")
        series = request.form.get("series")
        # get list of selected genre
        genre = ", ".join(request.form.getlist("genre"))
        pages = request.form.get("pages")
        status = request.form.get("status")
        bookmark = request.form.get("bookmark")

        if not bookmark:
            bookmark = 0

        # insert user inputs into library table
        cur.execute("INSERT INTO library(title, author, series, genre, pages_total, status, bookmark) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (title,
            author,
            series,
            genre,
            pages,
            status,
            bookmark)
         )

        # commit changes to database
        con.commit()

        return redirect("/library")
    else:

        return redirect("/library")

@app.route("/library/remove", methods=["POST"])
def remove_from_library():

    if request.method == "POST":

        title = request.form.get("title")

        # remove user inputted title from database
        cur.execute("DELETE FROM library WHERE title LIKE ?", (title,))

        # commit changes to database
        con.commit()

        return redirect("/library")
    else:
        return redirect("/library")

# save changes made during edit function
@app.route("/library/save", methods=["POST"])
def save_changes():
    # take list of bookmark and status
    # return books as dicts
    """
    books = NULL
    titles = "Halo: The Fall of Reach"
    status = "In progress"
    bookmark = 171
    # update sql table with new values

    for row in rows:
        cur.execute("UPDATE library SET status = ?, bookmark = ? WHERE title = ?", (status, bookmark, title))

    con.commit()
    """

    return redirect("/library")

# cancel changes made in the edit funtion
@app.route("/library/cancel", methods=["POST"])
def cancel_changes():
    return redirect("/library")

# wishlist will store wanted books and their prices
@app.route("/wishlist")
def wishlish():

    wishlist_db = cur.execute("SELECT * FROM wishlist").fetchall()

    wishlist = []


    for book in wishlist_db:

        wishlist.append({
            "title": book[0],
            "author": book[1],
            "market": f"£{book[2]:.2f}",
            "waterstone": f"£{book[3]:.2f}"
        })

    return render_template("wishlist.html", wishlist=wishlist)

@app.route("/wishlist/add", methods=["POST"])
def wishlish_add():

    title = request.form.get("title")
    author = request.form.get("author")
    market = request.form.get("market")

    waterstone = 0

    cur.execute("INSERT INTO wishlist(title, author, retail_price, amazon_price) VALUES(?, ?, ?, ?)",
        (title,
        author,
        market,
        waterstone)
    )

    con.commit()

    return redirect("/wishlist")

"""
@app.route("/wishlist/purchased", methods=["POST"])
def wishlist_clear():

    # get existing wishlist from wishlist database
    wishlist = cur.execute("SELECT * FROM wishlist").fetchall()

    #check_list = 0

    # look through wishlist
    for book in wishlist:

        # get current books check
        check = request.form.getlist("purchase")
        print(check)

        # check if row is checked
        if check == "on":

            cur.execute("DELETE FROM wishlist WHERE title = ?", (book[0],))



    con.commit()

    return redirect("/wishlist") """

@app.route("/tracker")
def tracker():
    return render_template("tracker.html")