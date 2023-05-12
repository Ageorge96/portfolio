import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@app.route("/index", methods=["POST"])
@login_required
def index():
    """Show portfolio of stocks"""

    if request.method == "GET":

        symbols = db.execute(
            "SELECT * FROM shares WHERE user_id = ?", session["user_id"]
        )

        # display users stock info in a table
        portfolio = []

        holding_total = 0

        # get user's name
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # get user's stock and shares info
        user_stock = db.execute(
            "SELECT * FROM shares WHERE user_id = ?", session["user_id"]
        )

        for row in user_stock:
            # get price of stock [name][price][symbol]
            stock = lookup(row["symbol"])

            # get total holdings for rows stock
            holding = float(row["shares_owned"]) * stock["price"]

            portfolio.append(
                {
                    "name": stock["name"],
                    "symbol": stock["symbol"],
                    "price": stock["price"],
                    "shares": row["shares_owned"],
                    "value": holding,
                }
            )

            # total user holding
            holding_total += float(holding)

        total = user[0]["cash"] + holding_total

        return render_template(
            "index.html",
            portfolio=portfolio,
            total=total,
            user=user[0],
            symbols=symbols,
        )

    elif request.method == "POST":

        # get user's details
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        action = request.form.get("action")
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not action:
            return apology("Please select an action...mow")

        if not symbol:
            return apology("Please select an owned stock...mow")

        # check for invalid orders
        if not shares.isdecimal():
            return apology("Invalid order...mow")

        shares = int(shares)

        quote = lookup(symbol)

        exchange = shares * quote["price"]

        dt = datetime.now()

        if action == "Buy":
            if user[0]["cash"] < exchange:
                return apology("Insufficient funds...mow")

            db.execute(
                "UPDATE users SET cash = (cash - ?) WHERE id = ?",
                exchange,
                session["user_id"],
            )
            db.execute(
                "UPDATE shares SET shares_owned = (shares_owned + ?) WHERE user_id = ? and symbol = ?",
                shares,
                session["user_id"],
                symbol,
            )
            db.execute(
                "INSERT INTO transactions(user_id, action, symbol, shares_exchanged, dot) VALUES(?, ?, ?, ?, ?)",
                session["user_id"],
                "Buy",
                symbol,
                shares,
                dt,
            )

        elif action == "Sell":
            valid_shares = db.execute(
                "SELECT * FROM shares WHERE user_id = ? and symbol = ?",
                session["user_id"],
                symbol,
            )

            if valid_shares[0]["shares_owned"] < shares:
                return apology("Insufficient shares...mow")

            db.execute(
                "UPDATE users SET cash = (cash + ?) WHERE id = ?",
                exchange,
                session["user_id"],
            )
            db.execute(
                "UPDATE shares SET shares_owned = (shares_owned - ?) WHERE user_id = ? and symbol = ?",
                shares,
                session["user_id"],
                symbol,
            )
            db.execute(
                "INSERT INTO transactions(user_id, action, symbol, shares_exchanged, dot) VALUES(?, ?, ?, ?, ?)",
                session["user_id"],
                "Sell",
                symbol,
                shares,
                dt,
            )

            check_shares = db.execute(
                "SELECT * FROM shares WHERE user_id = ? and symbol = ?",
                session["user_id"],
                symbol,
            )

            if check_shares[0]["shares_owned"] == 0:
                db.execute("DELETE FROM shares WHERE symbol = ?", symbol)

        else:
            return apology("Order could not be made...mow")

        symbols = db.execute(
            "SELECT * FROM shares WHERE user_id = ?", session["user_id"]
        )

        # display users stock info in a table
        portfolio = []

        holding_total = 0

        # get user's stock and shares info
        user_stock = db.execute(
            "SELECT * FROM shares WHERE user_id = ?", session["user_id"]
        )

        for row in user_stock:
            # get price of stock [name][price][symbol]
            stock = lookup(row["symbol"])

            # get total holdings for rows stock
            holding = float(row["shares_owned"]) * stock["price"]

            portfolio.append(
                {
                    "name": stock["name"],
                    "symbol": stock["symbol"],
                    "price": stock["price"],
                    "shares": row["shares_owned"],
                    "value": holding,
                }
            )

            # total user holding
            holding_total += float(holding)

        total = user[0]["cash"] + holding_total

        return render_template(
            "index.html",
            portfolio=portfolio,
            total=total,
            user=user[0],
            symbols=symbols,
        )
    else:
        return render_template("index.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # check if the user requests the page via GET
    if request.method == "GET":
        return render_template("buy.html")

    elif request.method == "POST":

        # get symbol input from user
        symbol = request.form.get("symbol")

        # get the requested stock from user
        shares = request.form.get("shares")

        if not symbol:
            return apology("Provide a symbol...mow")

        # check if the symbol exist in the database
        if not lookup(symbol):
            # alert the user that the symbol does not exist
            return apology("Invalid symbol...mow")

        if not shares:
            return apology("Provide shares order...mow")

        if not shares.isdecimal():
            return apology("Invalid order...mow")

        # get the stock price of the selected company
        quote = lookup(symbol)

        # get the users cash total from users table
        user_cash = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        order_cost = quote["price"] * float(shares)

        # check if the user has enough cash to buy shares
        if int(user_cash[0]["cash"]) < order_cost:
            # return apology if user does not have enough cash
            return apology("Insufficient funds...mow")

        # subtract purchase total from users cash
        db.execute(
            "UPDATE users SET cash = (cash - ?) WHERE id = ?",
            order_cost,
            session["user_id"],
        )

        orders = db.execute(
            "SELECT * FROM shares WHERE user_id = ? AND symbol = ?",
            session["user_id"],
            symbol,
        )

        # if user already has shares with company add to existing field
        if len(orders) == 0:
            # else enter purchase into shares database
            db.execute(
                "INSERT INTO shares(user_id, symbol, shares_owned) VALUES(?, ?, ?)",
                session["user_id"],
                symbol,
                shares,
            )

        else:
            db.execute(
                "UPDATE shares SET shares_owned = (shares_owned + ?) WHERE user_id = ?",
                shares,
                session["user_id"],
            )

        dt = datetime.now()

        db.execute(
            "INSERT INTO transactions(user_id, action, symbol, shares_exchanged, dot) VALUES(?, ?, ?, ?, ?)",
            session["user_id"],
            "Buy",
            symbol,
            int(shares),
            dt,
        )

        flash("Order has been made")

        return redirect("/")

    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # get data from history table
    history = db.execute(
        "SELECT * FROM transactions WHERE user_id = ?", session["user_id"]
    )

    # return history list with html
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username...mow", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password...mow", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password...mow", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")

    elif request.method == "POST":

        quote = lookup(request.form.get("symbol"))

        if not quote:
            return apology("Invalid symbol...mow")

        return render_template("quote.html", quote=quote)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":

        if not request.form.get("username"):
            return apology("Please provide a username...mow")

        elif not request.form.get("password"):
            return apology("Please provide a password...mow")

        elif not request.form.get("confirmation"):
            return apology("Please confirm password...mow")

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Password does not match...mow")

        rows = db.execute(
            "SELECT username FROM users WHERE username = ?",
            request.form.get("username"),
        )

        if len(rows) != 0:
            return apology("Username already exists...mow")

        user = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", user, hash)

        start_session = db.execute("SELECT * FROM users WHERE username = ?", user)

        session["user_id"] = start_session[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "GET":
        symbols = db.execute(
            "SELECT * FROM shares WHERE user_id = ?", session["user_id"]
        )
        return render_template("sell.html", symbols=symbols)

    elif request.method == "POST":

        # get symbol for sell
        symbol = request.form.get("symbol")
        sell_stock = lookup(symbol)

        # check that symbol exist
        if len(sell_stock) == 0:
            return apology("Invalid symbol...mow")

        # get sell order
        sell_order = request.form.get("shares")

        # check shares is an integer
        if not sell_order.isdecimal():
            return apology("Please enter integer only...mow")

        # get data from shares table for users sell request
        check_stock = db.execute("SELECT * FROM shares WHERE symbol = ?", symbol)

        # check if user has shares for this stock``
        if not check_stock:
            return apology(f"You own no stock with {symbol}...mow")

        sell_order = int(sell_order)

        # check user has enough shares for order
        user_shares = db.execute("SELECT * FROM shares WHERE symbol = ?", symbol)

        if user_shares[0]["shares_owned"] < sell_order:
            return apology("Insufficient shares...mow")

        # update user's shares
        db.execute(
            "UPDATE shares SET shares_owned = (shares_owned - ?) WHERE user_id = ?",
            sell_order,
            session["user_id"],
        )

        # update user's cash
        db.execute(
            "UPDATE users SET cash = (cash + (? * ?)) WHERE id = ?",
            sell_order,
            sell_stock["price"],
            session["user_id"],
        )

        # get the new shares value for that stock
        check_shares = db.execute(
            "SELECT * FROM shares WHERE user_id = ? and symbol = ?",
            session["user_id"],
            symbol,
        )

        # check if the user's shares is 0
        if check_shares[0]["shares_owned"] == 0:
            # delete row from table if shares is 0
            db.execute("DELETE FROM shares WHERE symbol = ?", symbol)

        dt = datetime.now()

        db.execute(
            "INSERT INTO transactions(user_id, action, symbol, shares_exchanged, dot) VALUES(?, ?, ?, ?, ?)",
            session["user_id"],
            "Sell",
            symbol,
            sell_order,
            dt,
        )

        flash("Sale complete")

        return redirect("/")

    else:
        return render_template("sell.html")
