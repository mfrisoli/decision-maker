import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def create_room(database, room_name, user_id):
            """Creates a Room and makes USER join room"""
            database.execute("INSERT INTO rooms (room_name, user_id)\
                    VALUES (:room_name, :user_id)",
                    room_name=room_name,
                    user_id=user_id)
            
            room_id = database.execute("SELECT MAX (room_id) AS room_id FROM rooms")

            database.execute("INSERT INTO roomjoins (room_id, user_id)\
                VALUES (:room_id, :user_id)",
                room_id=room_id[0]['room_id'],
                user_id=user_id)

    
    