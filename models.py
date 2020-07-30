from flask_sqlalchemy import SQLAlchemy
from app import app

# Configuration Values
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///datab_2.db' # Tells SQLalchemy how to connect to the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Institiate the Database Object
db = SQLAlchemy(app)

class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hash = db.Column(db.String(), nullable=False)

    rooms = db.relationship('Rooms', backref='users')
    votes = db.relationship('Votes', backref='users')
    roomjoins = db.relationship('Roomjoins', backref='users')


class Rooms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(10), default='edit', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    options = db.relationship('Options', backref='rooms')
    votes = db.relationship('Votes', backref='rooms')
    roomjoins = db.relationship('Roomjoins', backref='rooms')

class Options(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)

    votes = db.relationship('Votes', backref='options')

class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vote = db.Column(db.Integer())
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)


class Roomjoins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10), nullable=False, default='join')
    voted = db.Column(db.String(4), nullable=False, default='no')
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)





