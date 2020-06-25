/* Create User Table */
CREATE TABLE 'users' (
    'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'username' VARCHAR(255) NOT NULL UNIQUE, 
    'hash' TEXT NOT NULL
    );

/* Create User ROOMS */
CREATE TABLE rooms (
    'room_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'room_name' VARCHAR(255) NOT NULL UNIQUE,
    'user_id' INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES 'users' ('id')
    );

/* Create Options Table */
CREATE TABLE options (
    'option_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'option_name' VARCHAR(255) NOT NULL,
    'room_id' INTEGER NOT NULL,
    FOREIGN KEY (room_id) REFERENCES 'rooms' ('room_id')
    );

CREATE TABLE voting (
    'vote_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'option_id' VARCHAR(255) NOT NULL,
    'vote' INTERGER NOT NULL,
    'user_id' INTEGER NOT NULL,
    'room_id' INTEGER NOT NULL,
    FOREIGN KEY (room_id) REFERENCES 'rooms' ('room_id')
    );

CREATE TABLE roomjoins (
    'roomjoin_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'room_id' INTEGER NOT NULL,
    'user_id' INTEGER NOT NULL,
    'status' TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES 'users' ('id')
    );

/*

CREATE TABLE 'transactions' ('tran_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'timestamp' DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 'user_id' INTERGER NOT NULL,'symbol' VARCHAR(10) NOT NULL,'share_price' INTERGER NOT NULL, 'shares' INTERGER NOT NULL,'share_cost' INTERGER NOT NULL, 'buy_sell' VARCHAR(4) NOT NULL,FOREIGN KEY (user_id) REFERENCES 'users' ('id'))

CREATE TABLE 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL, 'cash' NUMERIC NOT NULL DEFAULT 10000.00 )

*/