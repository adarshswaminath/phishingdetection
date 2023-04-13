import sqlite3

# create a new database file
conn = sqlite3.connect('database.db')

# create a table to store usernames and passwords
conn.execute('''CREATE TABLE users
             (username TEXT PRIMARY KEY,
              password TEXT);''')

# insert the usernames and corresponding passwords
usernames = ['Apple', 'Bat', 'Cat', 'Dog', 'Ear', 'Fan', 'Goat', 'House', 'Ice', 'Joker', 'Kite']
for username in usernames:
    password = username
    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

# commit the changes and close the connection
conn.commit()
conn.close()
