/* Create User Table */
CREATE TABLE 'users' (
    'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'username' VARCHAR(50) NOT NULL UNIQUE, 
    'hash' TEXT NOT NULL
    );

/* Create User ROOMS status= [edit, open, closed]*/
CREATE TABLE rooms (
    'room_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    'room_name' VARCHAR(50) NOT NULL,
    'user_id' INTEGER NOT NULL,
    'status' TEXT NOT NULL DEFAULT 'edit',
    FOREIGN KEY (user_id) REFERENCES 'users' ('id')
    );

/* Create Options Table */
CREATE TABLE options (
    'option_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'option_name' VARCHAR(50) NOT NULL,
    'room_id' INTEGER NOT NULL,
    FOREIGN KEY (room_id) REFERENCES 'rooms' ('room_id')
    );

/* Voting Table */
CREATE TABLE voting (
    'vote_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'option_id' VARCHAR(255) NOT NULL,
    'vote' INTEGER NOT NULL,
    'user_id' INTEGER NOT NULL,
    'room_id' INTEGER NOT NULL,
    FOREIGN KEY (room_id) REFERENCES 'rooms' ('room_id')
    );

/* Track the rooms where the user has joined status: [default=join, leave], voted=[no, yes]  */
CREATE TABLE roomjoins (
    'roomjoin_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'room_id' INTEGER NOT NULL,
    'user_id' INTEGER NOT NULL,
    'status' TEXT NOT NULL,
    'voted' TEXT NOT NULL DEFAULT 'no',
    FOREIGN KEY (user_id) REFERENCES 'users' ('id')
    );
