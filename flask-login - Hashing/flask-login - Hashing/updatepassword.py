import bcrypt
from flask import Flask, render_template, request, redirect, url_for
import re
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

connection = None

def getCursor(dictionary_cursor=False):
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, password=connect.dbpass, host=connect.dbhost, database=connect.dbname, autocommit=True)
    cursor = connection.cursor(dictionary=dictionary_cursor)
    return cursor


def get_all_users():
    cursor = getCursor()
    cursor.execute("SELECT * FROM secureusers") 
    users = cursor.fetchall()
    return users

def update_hashed_password(user_id, hashed_pw):
    cursor = getCursor()
    cursor.execute("UPDATE secureusers SET password = %s WHERE user_id = %s", (hashed_pw, user_id))
    

users = get_all_users()
for user in users:
    user_id = user[0]
    plain_password = user[1]
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    update_hashed_password(user_id, hashed_pw.decode('utf-8'))

if __name__ == '__main__':
    app.run(debug=True)