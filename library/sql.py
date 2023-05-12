import sqlite3

con = sqlite3.connect("media.db")

cur = con.cursor()

library = cur.execute("SELECT * FROM library;").fetchall()

books = []

for book in library:

    books.append({
        "title": book[1],
        "author": book[2],
        "series": book[3],
        "genre": book[4],
        "pages": book[5],
        "status": book[6],
        "bookmark": book[7]
    })

print(books[1]["pages"])
"""
CREATE TABLE library (
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    series TEXT DEFAULT "N/A",
    genre TEXT NOT NULL,
    pages_total INTEGER,
    status TEXT,
    bookmark INTEGER DEFAULT 0 NOT NULL
);

CREATE TABLE wishlist (
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    retail_price REAL NOT NULL,
    amazon_price REAL NOT NULL,
);

INSERT INTO library (title, author, series, genre, pages_total, status, bookmark)
SELECT (title, author, series, genre, pages_total, status, bookmark)
FROM trans;


INSERT INTO library(title, author, series, genre, pages_total, status, bookmark)
VALUES("Test", "test", "test", "test", 100, "test", 1);

CREATE TABLE wishlist (
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    market_price REAL NOT NULL,
    current_amz REAL NOT NULL,
    )

"""
