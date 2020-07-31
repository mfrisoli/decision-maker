import os

from cs50 import SQL
from models import  Users, Rooms, Options, Votes, Roomjoins, app, db
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import desc
from sqlalchemy.sql import func

from helpers import apology, login_required, create_room


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Search for rooms
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Display Welcome message and box to search rooms
    if request.method == "GET":
        return render_template("index.html", search=False)
    else:
        room_id = request.form.get("room_id")

            #room = db.execute("SELECT * FROM rooms WHERE room_id=:room_id", room_id=room_id)

        room = Rooms.query.filter_by(id=room_id).first()


        if not room:
            return render_template("index.html", search=False, message="Room not Found")

        else:
            return render_template("index.html", room=room, search=True)



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
        #rows = db.execute("SELECT * FROM users WHERE username = :username",
        #                  username=request.form.get("username"))

        user = Users.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user.id
        session["username"] = user.username

        # Redirect user to home page
        return redirect(url_for('index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for('index'))

@app.route("/create", methods=["GET", "POST"])
@login_required
def createroom():
    """Create Room"""

    # if Method is GET Display Room list
    if request.method == "GET":
        return render_template("create.html")
    # Else
    else:
        # room_name = request.form.get("room_name")
        # create_room(db, room_name, session['user_id'])
        
        # Create Room
        room = Rooms(name=request.form.get("room_name"), user_id=session['user_id'])  
        db.session.add(room)
        db.session.commit()
        
        # Make user Join room
        join_room = Roomjoins(room_id=room.id, user_id=session['user_id'])
        db.session.add(join_room)
        db.session.commit()
         #room_id = db.execute("SELECT MAX (room_id) AS room_id FROM rooms")
        session['edit_room'] = room.id

        return redirect(url_for('add_list'))

@app.route("/rooms", methods=["GET", "POST"])
@login_required
def show_rooms():
    if request.method == "GET":
        # Room user owns and moderates
            #rooms = db.execute("SELECT * FROM rooms WHERE user_id=:user_id", user_id=session['user_id'])
        rooms = Rooms.query.filter_by(user_id=session['user_id']).all()

        # Rooms user is part of and can vote
            #rooms_joins = db.execute("SELECT * FROM rooms WHERE room_id IN (SELECT room_id FROM roomjoins WHERE user_id=:user_id AND status='join')", user_id=session['user_id'])
        rooms_joins = Roomjoins.query.filter_by(user_id=session['user_id'], status='join').all()
        return render_template("rooms.html", rooms=rooms, rooms_joins=rooms_joins)

    else:
        room_id = request.form.get("room_id")

        if(request.form.get("option") == "edit"):
            
            # Go to create list:
            session['edit_room'] = room_id

            return redirect(url_for('add_list'))

        elif (request.form.get("option") == "reset"):
            # Reset all votes on the list
                #db.execute("DELETE FROM voting WHERE room_id=:room_id", room_id=room_id)
            Votes.query.filter_by(room_id=room_id).delete()
            db.session.commit()

            # Change Status of room to open
                #db.execute("UPDATE rooms SET status='open' WHERE room_id=:room_id", room_id=room_id)
            update = Rooms.query.filter_by(id=room_id).first()
            update.status = 'open'
            db.session.commit()

            # reset user vote voted to no
                #db.execute("UPDATE roomjoins SET voted='no' WHERE room_id=:room_id",
                #room_id=room_id
                #)
            update = Roomjoins.query.filter_by(room_id=room_id).first()
            update.voted = 'no'
            db.session.commit()

            return redirect(url_for('show_rooms'))

        elif (request.form.get("option") == "close"):
            # Close Room
                #db.execute("UPDATE rooms SET status='close' WHERE room_id=:room_id", room_id=room_id)
            update = Rooms.query.filter_by(id=room_id).first()
            update.status = 'close'
            db.session.commit()

            return redirect(url_for('show_rooms'))

        elif (request.form.get("option") == "delete"):

            # Delete Room, Votes and Options
            
            # Delete Options:
                #db.execute("DELETE FROM options WHERE room_id=:room_id", room_id=room_id)
            Options.query.filter_by(room_id=room_id).delete()
            db.session.commit()          

            # Delete roomsjoins table
                #db.execute("DELETE FROM roomjoins WHERE room_id=:room_id", room_id=room_id)
            Roomjoins.query.filter_by(room_id=room_id).delete()
            db.session.commit()

            # delete votes
                #db.execute("DELETE FROM voting WHERE room_id=:room_id", room_id=room_id)
            Votes.query.filter_by(room_id=room_id).delete()
            db.session.commit()
        
            # Delete room table
                #db.execute("DELETE FROM rooms WHERE room_id=:room_id", room_id=room_id)
            Rooms.query.filter_by(id=room_id).delete()
            db.session.commit()

            return redirect(url_for('show_rooms'))

        elif request.form.get("option_joins") == "dashboard":

            session['edit_room'] = room_id

            return redirect(url_for('dashboard'))

        elif request.form.get("option_joins") == "leave":
            # leave room and render again /rooms
            room_id = request.form.get("room_id")
            user_id = session['user_id']

                #db.execute("UPDATE roomjoins SET status='leave' WHERE room_id=:room_id AND user_id=:user_id", room_id=room_id, user_id=user_id)
            update = Roomjoins.query.filter_by(room_id=room_id, user_id=user_id).first()
            update.status = 'leave'
            db.session.commit()

            return redirect(url_for('show_rooms'))


@app.route("/modifylist", methods=["GET", "POST"])
@login_required
def edit_list():

    if request.method =="GET":

        room_id = session['edit_room']
        room_options = db.execute("SELECT * FROM options WHERE room_id=:room_id", room_id=room_id)
        room_options = Options.query.filter_by(room_id=room_id).all()

            #room = db.execute("SELECT * FROM rooms WHERE room_id=:room_id", room_id=room_id)
        room = Rooms.query.filter_by(id=room_id).first()

        return render_template("showlist.html", room=room_options, room_name=room.name, room_id=room_id)
    
    else:

        room_id = request.form.get("room_id")
            #db.execute("UPDATE rooms SET status='edit' WHERE room_id=:room_id", room_id=room_id)
        Rooms.query.filter_by(id=room_id).update( {Rooms.status: 'edit' } )
        db.session.commit()

        session['edit_room'] = room_id

        # Update user in the room status to not voted
            #db.execute("UPDATE roomjoins SET voted='no' WHERE room_id=:room_id",
            #    room_id=room_id
            #    )
        Roomsjoins.query.filter_by(room_id=room_id).update( {Roomjoins.voted: 'no'} )
        db.session.commit()

        # Delete votes
            # db.execute("DELETE FROM voting WHERE room_id=:room_id", room_id=room_id)
        Votes.query.filter_by(room_id=room_id).delete()
        db.session.commit()


        return redirect(url_for('add_list'))


@app.route("/createlist", methods=["GET", "POST"])
@login_required
def add_list():
    if request.method == "GET":
        # check if room is already voting or closed, else it can be modified
        room_id = session['edit_room']
            #room_options = db.execute("SELECT * FROM options WHERE room_id=:room_id", room_id=room_id)
        room_options = Options.query.filter_by(room_id=room_id).all()
        
            #room = db.execute("SELECT * FROM rooms WHERE room_id=:room_id", room_id=room_id)
        room = Rooms.query.filter_by(id=room_id).first()

        if room.status == 'edit':

            return render_template("createlist.html", room=room_options, room_name=room.name, room_id=room_id)
        
        else:
            
            # room_id = session['edit_room']
            return redirect(url_for('edit_list'))

    else:
        if request.form.get("add") == "add":
            new_option = request.form.get("option")
            room_id = session['edit_room']

            # Add Option to option table
                #db.execute("INSERT INTO options (option_name, room_id) VALUES (:option_name, :room_id)", option_name=new_option, room_id=room_id)
            option = Options(name=new_option, room_id=room_id)
            db.session.add(option)
            db.session.commit()

            return redirect(url_for('add_list'))

        else:
            option_id = request.form.get("change") # option_id

            # Remove Option from options table option_id
                #db.execute("DELETE FROM options WHERE option_id=:option_id", option_id=option_id)
            option = Options.query.filter_by(id=option_id).first()
            db.session.delete(option)
            db.session.commit()

            return redirect(url_for('add_list'))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html", error="")
    else:
        # Get new user details
        username = request.form.get("username")
        hash_pass = generate_password_hash(request.form.get("password"))
        
        # Check if user already exists
        user = Users.query.filter_by(username=username).first()

            #user_registered = db.execute("SELECT * FROM users WHERE users.username=:username", username=username)

        if user:

            return render_template("register.html", error="Sorry..user Name already exists")
        
        # Else Continue and Add User
        user = Users(username=username, hash=hash_pass)
        db.session.add(user)
        db.session.commit()

            #db.execute("INSERT INTO users (username, hash)\
            #         VALUES (:username, :hash)",
            #         username=username,
            #         hash=hash_pass)

        return redirect(url_for('login'))


@app.route("/godashboard")
@login_required
def godashboard():
    room_id = request.args['room_id_join']
    session["edit_room"] = room_id

    # Check if user is already in this room or has ever been in the room:
        #in_room = db.execute("SELECT * FROM roomjoins WHERE room_id=:room_id AND user_id=:user_id", room_id=room_id, user_id=session['user_id'])
    in_room = Roomjoins.query.filter_by(room_id=room_id, user_id=session['user_id']).first()


    if not in_room:
        # Add user to room
            #db.execute("INSERT INTO roomjoins (room_id, user_id, status)\
            #           VALUES (:room_id, :user_id, :status)",
            #           room_id=room_id,
            #           user_id=session['user_id'],
            #           status="join"
            #           )

        user_to_room = Roomjoins(room_id=room_id, user_id=session['user_id'])
        db.session.add(user_to_room)
        db.session.commit()

    else:
        # update user to join 
        user_to_room = in_room
        user_to_room.status = 'join'
        db.session.commit()
            #db.execute("UPDATE roomjoins SET status='join' WHERE room_id=:room_id AND user_id=:user_id",
            #            room_id=room_id,
            #            user_id=session['user_id']
            #            )
    if request.args["index_join"] != "yes":
            #db.execute("UPDATE rooms SET status='open' WHERE room_id=:room_id AND user_id=:user_id",
            #           room_id=room_id,
            #           user_id=session['user_id']
            #           )
        room_status = Rooms.query.filter_by(id=room_id, user_id=session['user_id']).first()
        room_status.status = 'open'
        db.session.commit()

    return redirect(url_for('dashboard'))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():


    if request.method == "GET":
        # Get Room and Room Options information

        room_id = session['edit_room']
            #room = db.execute("SELECT * FROM rooms WHERE room_id=:room_id", room_id=room_id)
        room = Rooms.query.filter_by(id=room_id).first()
            #options = db.execute("SELECT * FROM options WHERE room_id=:room_id", room_id=room_id)
        options = Options.query.filter_by(room_id=room_id).all()
            #room_user_data = db.execute("SELECT * FROM roomjoins WHERE room_id=:room_id AND user_id=:user_id", room_id=room_id, user_id=session['user_id'])
        room_user_data = Roomjoins.query.filter_by(room_id=room_id, user_id=session['user_id']).first()

        # Room is open:
        room_status = room.status
        user_voted = room_user_data.voted == 'yes'
        in_room = room_user_data.status == 'join'

        # Check if user is in the room:
        if not in_room:
            # User not in the room display apology
            return apology("you are not in this room")

        # User is in the room, continue

        # if room is open 
        if room_status == "open":
            if not user_voted:
                # Ask user to vote:
                session['edit_room'] = room_id
                return render_template('dashboard_vote.html', room=room, options=options)
            
            # user voted -> Show user result only
            else:
                message = "These are your Votes!, to see the Room Results \
                           you have to wait the voting finishes!"
                # Show dashboard with user result
                    #user_votes = db.execute("SELECT options.option_id, options.option_name, voting.vote \
                    #            FROM voting\
                    #            JOIN options ON voting.option_id=options.option_id\
                    #            WHERE voting.user_id=:user_id AND voting.room_id=:room_id",
                    #            user_id=session["user_id"],
                    #            room_id=room_id)

                user_votes = Votes.query.filter_by(user_id=session["user_id"], room_id=room_id).all()
                
                return render_template("dashboard_result.html",
                                        user_votes=user_votes,
                                        room=room,
                                        room_close=False,
                                        user_voted=user_voted,
                                        message=message
                                        )

        # else if Room is open or close and user voted -> Show Dashboard with ALL results
        elif room_status == "close":
            if not user_voted:
                # Show results and tell user it did not vote:
                message = "You did not Vote! but these are the Results!"
                    #room_votes = db.execute("SELECT options.option_name, SUM (voting.vote) AS all_votes \
                    #    FROM voting \
                    #    JOIN options ON voting.option_id=options.option_id \
                    #    WHERE options.room_id=:room_id\
                    #    GROUP BY (options.option_name) \
                    #    ORDER BY all_votes DESC",
                    #    room_id=room_id)
                # Get Query Data
                room_votes = db.session.query(Options, func.sum(Votes.vote).label('total')).join(Options.votes).filter(Votes.room_id==room_id).group_by(Votes.option_id).order_by(desc('total')).all()

                # Convert List(tuple) in to List(Dict)
                room_results = []
                for row in room_votes:
                    room_results.append({'option_name':row[0].name, 'all_votes':row[1]})
            

                return render_template("dashboard_result.html",
                                        room_votes= room_results,
                                        room=room,
                                        room_close=True,
                                        user_voted=user_voted,
                                        message=message
                                        )

            
            # Show all results
            else:
                # Show dashboard with user result
                message = "Here are your votes and the Results!"

                # User Votes:
                    #user_votes = db.execute("SELECT options.option_id, options.option_name, voting.vote\
                    #    FROM voting\
                    #    JOIN options ON voting.option_id=options.option_id\
                    #    WHERE voting.user_id=:user_id AND voting.room_id=:room_id",
                    #    user_id=session["user_id"],
                    #    room_id=room_id)

                user_votes = Votes.query.filter_by(user_id=session["user_id"], room_id=room_id).all()

                # Room Results
                #TODO check if there is a tie
                        #room_votes = db.execute("SELECT options.option_name, SUM (voting.vote) AS all_votes\
                        #    FROM voting \
                        #    JOIN options ON voting.option_id=options.option_id \
                        #    WHERE options.room_id=:room_id\
                        #    GROUP BY (options.option_name) \
                        #    ORDER BY all_votes DESC",
                        #    room_id=room_id
                        #    )

                room_votes = db.session.query(Options, func.sum(Votes.vote).label('total')).join(Options.votes).filter(Votes.room_id==room_id).group_by(Votes.option_id).order_by(desc('total')).all()

                # Convert List(tuple) in to List(Dict)
                room_results = []
                for row in room_votes:
                    room_results.append({'option_name':row[0].name, 'all_votes':row[1]})

                # Create pie chart list
                chart_list = [["Option", "Vote"]]
                for row in room_results:
                    chart_list.append([row['option_name'], row['all_votes']])
    
                return render_template("dashboard_result.html",
                    room_votes=room_results,
                    user_votes=user_votes,
                    room=room,
                    room_close=True,
                    user_voted=user_voted,
                    message=message,
                    chart_list=chart_list)

        # Else room is being edited
        else:
            return apology("room is being edited and not available for voting!")

    # else request.method="POST"      
    else:

        # Room Details
        room_id = session['edit_room']
            #room = db.execute("SELECT * FROM rooms WHERE room_id=:room_id", room_id=room_id)
        room = Rooms.query.filter_by(id=room_id).first()
            #options = db.execute("SELECT * FROM options WHERE room_id=:room_id", room_id=room_id)
        options = Options.query.filter_by(room_id=room_id).all()
        
            #room_user_data = db.execute("SELECT * FROM roomjoins WHERE room_id=:room_id AND user_id=:user_id", room_id=room_id, user_id=session['user_id'])

        room_user_data = Roomjoins.query.filter_by(room_id=room_id, user_id=session['user_id']).first()

        # get Post Results and store in data base
        for row in options:

            vote = request.form.get(str(row.id))

            cast_vote = Votes(vote=vote, option_id=row.id, user_id=session['user_id'], room_id=room_id)
            db.session.add(cast_vote)
            db.session.commit()
                #db.execute("INSERT INTO voting (option_id, vote, user_id, room_id)\
                #    VALUES (:option_id, :vote, :user_id, :room_id)",
                #    option_id=row['option_id'],
                #    vote=vote,
                #    user_id=session['user_id'],
                #    room_id=room_id
                #    )

        # Change user to voted="yes"
        user_vote_status = Roomjoins.query.filter_by(room_id=room_id, user_id=session['user_id']).first()
        user_vote_status.voted = 'yes'
        db.session.commit()

            #db.execute("UPDATE roomjoins SET voted='yes' WHERE room_id=:room_id AND user_id=:user_id",
            #            room_id=room_id,
            #            user_id=session['user_id']
            #            )
            #            
        return redirect(url_for('dashboard'))


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)



# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run()
