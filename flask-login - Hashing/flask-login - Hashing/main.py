import bcrypt
from flask import Flask, render_template, request, redirect, url_for,session
import re
import mysql.connector
from mysql.connector import FieldType
import connect


app = Flask(__name__)
app.secret_key = 'zxw secret key'

connection = None



def getCursor(dictionary_cursor=False):
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, password=connect.dbpass, host=connect.dbhost, database=connect.dbname, autocommit=True)
    cursor = connection.cursor(dictionary=dictionary_cursor)
    return cursor

def encrypt_password(plain_password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')

def encrypt_all_user_passwords():
    cursor = getCursor()
    cursor.execute("SELECT * FROM secureusers")
    users = cursor.fetchall()

    for user in users:
        user_id = user[0]
        plain_password = user[4]


        hashed_pw = encrypt_password(plain_password)
        cursor.execute("UPDATE secureusers SET password = %s WHERE user_id = %s", (hashed_pw, user_id))

encrypt_all_user_passwords()



# http://localhost:5000/login/ - this will be the login page, we need to use both GET and POST requests
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    cursor = getCursor(dictionary_cursor=True)
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        user_password = request.form['password']
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM secureusers WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account is not None:
            databasepassword = account['password']
            if bcrypt.checkpw(user_password.encode('utf-8'), databasepassword.encode()):
            # If account exists in accounts table in out database
            # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['user_id'] = account['user_id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                #password incorrect
                msg = 'Incorrect password!'
        else:
            # Account doesnt exist or username incorrect
            msg = 'Incorrect username'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))





# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    cursor = getCursor(dictionary_cursor=True)
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phone_number']
        email = request.form['email']
        role_name= request.form['role_name']
        # Check if account exists using MySQL
  
        cursor.execute('SELECT * FROM  secureusers  WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
          
            password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            print(password)
            cursor.execute('INSERT INTO secureusers (username, name, email, password, phone_number, role_name) VALUES ( %s, %s, %s, %s, %s, %s)', (username,name,email,password,phone_number,role_name))
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = getCursor()
        cursor.execute('SELECT * FROM secureaccount WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)