import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, create_room

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


# Search for rooms
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Display Welcome message and box to search rooms
    if request.method == "GET":
        return render_template("index.html", search=False)
    else:
        room_id = request.form.get("room_id")

        room = db.execute("SELECT * FROM rooms WHERE room_id=:room_id", room_id=room_id)


        if len(room) != 1:
            return render_template("index.html", search=False, message="Room not Found")

        else:
            return render_template("index.html", room=room, search=True)
       # TODO: Join room
       # TODO: see rooms your are in show VOTING ACTIVE/POLL CLOSED
       # TODO: Vote in room
       # TODO: See results


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

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

@app.route("/create", methods=["GET", "POST"])
@login_required
def createroom():
    """Create Room"""

    # if Method is GET Display Room list
    if request.method == "GET":
        return render_template("create.html")
    # Else 
    else:
        room_name = request.form.get("room_name")

        create_room(db, room_name, session['user_id'])

        room_id = db.execute("SELECT MAX (room_id) AS room_id FROM rooms")
        session['edit_room'] = room_id[0]['room_id']

        return redirect("/createlist")

@app.route("/rooms", methods=["GET", "POST"])
@login_required
def show_rooms():
    if request.method == "GET":
        # Room user owns and moderates
        rooms = db.execute("SELECT * FROM rooms WHERE user_id=:user_id", user_id=session['user_id'])

        # Rooms user is part of and can vote
        rooms_joins = db.execute("SELECT * FROM rooms WHERE room_id IN (SELECT room_id FROM roomjoins WHERE user_id=:user_id AND status='join')", user_id=session['user_id'])

        return render_template("rooms.html", rooms=rooms, rooms_joins=rooms_joins)

    else:
        if(request.form.get("option") == "edit"):
            # Go to create list:
            room_id = request.form.get("room_id")
            session['edit_room'] = room_id

            return redirect("/createlist")

        elif (request.form.get("option") == "reset"):
            # TODO: Reset all votes on the list?

            return apology("TODO")
            
        elif (request.form.get("option") == "delete"):

            # Delete Room, Votes and Options
            room_id = request.form.get("room_id")
            
            # Delete Options:
            db.execute("DELETE FROM options WHERE room_id=:room_id", room_id=room_id)           

            # Delete room table
            db.execute("DELETE FROM rooms WHERE room_id=:room_id", room_id=room_id)

            # Delete roomsjoins table
            db.execute("DELETE FROM roomjoins WHERE room_id=:room_id", room_id=room_id)

            # delete votes
            db.execute("DELETE FROM voting WHERE room_id=:room_id", room_id=room_id)

            return redirect("/rooms")

        elif request.form.get("option_joins") == "dashboard":

            session['edit_room'] = request.form.get("room_id")

            return redirect("/dashboard")

        elif request.form.get("option_joins") == "leave":
            # leave room and render again /rooms
            room_id = request.form.get("room_id")
            user_id = session['user_id']

            db.execute("UPDATE roomjoins SET status='leave' WHERE room_id=:room_id AND user_id=:user_id", room_id=room_id, user_id=user_id)

            return redirect("/rooms")


@app.route("/createlist", methods=["GET", "POST"])
@login_required
def add_list():
    if request.method == "GET":
        # TODO: check if room is already voting or closed, else it can be modified
        room_id = session['edit_room']
        room_options = db.execute("SELECT * FROM options WHERE room_id=:room_id", room_id=room_id)
        room = db.execute("SELECT * FROM rooms WHERE room_id=:room_id", room_id=room_id)

        if room[0]['status'] == 'edit':

            return render_template("createlist.html", room=room_options, room_name=room[0]['room_name'], room_id=room_id)
        
        else:
            return render_template("showlist.html", room=room_options, room_name=room[0]['room_name'],  room_id=room_id)

    else:
        if request.form.get("add") == "add":
            new_option = request.form.get("option")
            room_id = session['edit_room']

            # Add Option to option table
            db.execute("INSERT INTO options (option_name, room_id) VALUES (:option_name, :room_id)", option_name=new_option, room_id=room_id)
            
            return redirect("/createlist")

        else:
            option_id = request.form.get("change") # option_id

            # Remove Option from options table option_id
            db.execute("DELETE FROM options WHERE option_id=:option_id", option_id=option_id)

            return redirect("/createlist")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Check if user already exists
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        hash_pass = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash)\
            VALUES (:username, :hash)",
            username=username,
            hash=hash_pass)

        return redirect("/login")


@app.route("/godashboard")
@login_required
def godashboard():
    room_id = request.args['room_id_join']
    session["edit_room"] = room_id

    # TODO: Check if user is already in this room:
    # db.execute("SELECT * FROM roomjoins WHERE room_id=:room_id AND user_id=:user_id", room_id=room_id, user_id=session['user_id'])


    return redirect("/dashboard")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():


    if request.method == "GET":
        # Get Room and Room Options information

        room_id = session['edit_room']
        room = db.execute("SELECT * FROM rooms WHERE room_id=:room_id", room_id=room_id)
        options = db.execute("SELECT * FROM options WHERE room_id=:room_id", room_id=room_id)

        # Check if user voted

        # check if poll is open or close

        return render_template('dashboard.html', room=room, options=options)
    else:
        return apology("not working")




def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)



# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
