import bcrypt
from flask import Flask, render_template, request, redirect, url_for,session,flash
import re
import mysql.connector
from mysql.connector import FieldType
import connect
from werkzeug.utils import secure_filename
import os


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
        
        if not plain_password.startswith('$2b$'):
            hashed_pw = encrypt_password(plain_password)
            cursor.execute("UPDATE secureusers SET password = %s WHERE user_id = %s", (hashed_pw, user_id))


encrypt_all_user_passwords()

# http://localhost:5000/ - main page
@app.route('/')
def index():
    # check if user has loggin 
    if 'loggedin' in session:
        # if user already login it goes to home page
        return redirect(url_for('home'))
    else:
        # if not login it goes to login page
        return redirect(url_for('login'))

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
                session['role_name'] = account['role_name']
                # Redirect to home page
                if account['role_name'] == 'staff-admin':
                   return redirect(url_for('admin'))
                elif account['role_name'] == 'staff':
                   return redirect(url_for('staff'))
                else:
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
   session.pop('user_id', None)
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
            cursor.execute('INSERT INTO secureusers (username, name, email, password, phone_number, role_name) VALUES ( %s, %s, %s, %s, %s, %s)', (username,name,email,password,phone_number,'customer'))
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    cursor = getCursor(dictionary_cursor=True)
    # Check if user is logged in
    if 'loggedin' in session and session.get('role_name') == 'customer':
        # User is logged in, show them the home page
        username = session['username']
        cursor.execute('SELECT * FROM secureusers WHERE username = %s', (username,))
        account = cursor.fetchone()

        # Retrieve holiday houses data from database
        cursor.execute('SELECT * FROM holiday_houses')
        holiday_houses = cursor.fetchall()

        # Render the home template with account, username, and holiday houses data
        return render_template('home.html', account=account, username=username, holiday_houses=holiday_houses)
    
    # User is not logged in, redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/staffhome')
def staffhome():
    cursor = getCursor(dictionary_cursor=True)
    # Check if user is logged in
    if 'loggedin' in session and (session.get('role_name') == 'staff' or session.get('role_name') == 'staff-admin'):

        # User is logged in, show them the home page
        username = session['username']
        cursor.execute('SELECT * FROM secureusers WHERE username = %s', (username,))
        account = cursor.fetchone()

        # Retrieve holiday houses data from database
        cursor.execute('SELECT * FROM holiday_houses')
        holiday_houses = cursor.fetchall()

        # Render the home template with account, username, and holiday houses data
        return render_template('staffhome.html', account=account, username=username, holiday_houses=holiday_houses)
    
    # User is not logged in, redirect to login page
    return redirect(url_for('login'))




@app.route('/add_house', methods=['GET', 'POST'])
def add_house():
    cursor = getCursor(dictionary_cursor=True)
   
    if 'loggedin' in session and (session.get('role_name') == 'staff' or session.get('role_name') == 'staff-admin'):
        if request.method == 'POST':
            house_address = request.form['house_address']
            number_of_bedrooms = request.form['number_of_bedrooms']
            number_of_bathrooms = request.form['number_of_bathrooms']
            maximum_occupancy = request.form['maximum_occupancy']
            rental_per_night= request.form['rental_per_night']
   
            if 'house_image' in request.files:
                house_image = request.files['house_image']
                if house_image.filename != '':
                    filename = secure_filename(house_image.filename)
                    house_image.save(os.path.join('path/to/save', filename))
                    # 存储图片的文件名或路径到数据库

           
            cursor.execute('INSERT INTO holiday_houses (house_address, number_of_bedrooms, number_of_bathrooms,maximum_occupancy,rental_per_night,house_image) VALUES (%s, %s, %s, %s,%s, %s,)', 
                           (house_address, number_of_bedrooms, number_of_bathrooms,maximum_occupancy,rental_per_night,house_image))

            flash('New holiday house added successfully!')
            return redirect(url_for('staffhome'))

        # 如果是 GET 请求，显示添加房屋的表单
        return render_template('add_house_form.html')

    # 如果用户未登录，重定向到登录页面
    return redirect(url_for('login'))


# @app.route('/edit_house/<int:house_id>', methods=['GET', 'POST'])
# def edit_house(house_id):
#     if request.method == 'POST':
#         # 更新数据库中的房屋信息
#         # ...
#         return redirect(url_for('staffhome'))
#     # 获取房屋的当前信息以填充表单
#     # ...
#     return render_template('edit_house_form.html', house=house)


# @app.route('/delete_house/<int:house_id>')
# def delete_house(house_id):
#     # 从数据库中删除房屋
#     # ...
#     return redirect(url_for('staffhome'))



@app.route('/profile')
def profile():
    cursor = getCursor(dictionary_cursor=True)
    # Check if user is loggedin
    if 'loggedin' in session :
        # User is loggedin show them the home page
        username=session['username']
        cursor.execute('SELECT * FROM  secureusers  WHERE username = %s', (username,))
        account = cursor.fetchone()
        cursor.execute('SELECT c.address FROM secureusers AS s JOIN customer AS c ON s.user_id=c.user_id WHERE s.username = %s', (username,))
        customer = cursor.fetchone()
        return render_template('profile.html', account=account, username=username, customer=customer )
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/update_profile', methods=["GET", "POST"])
def update_profile():
    if 'loggedin' in session:
        username = session['username']
        cursor = getCursor(dictionary_cursor=True)

        if request.method == 'GET':
            cursor.execute('SELECT * FROM secureusers WHERE username = %s', (username,))
            account = cursor.fetchone()
            cursor.execute('SELECT c.address FROM secureusers AS s JOIN customer AS c ON s.user_id=c.user_id WHERE s.username = %s', (username,))
            customer = cursor.fetchone()
            return render_template('updateprofile.html', account=account, customer=customer)

        elif request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            new_password = request.form.get('new_password')
            address = request.form.get('address')

            # Only update the password if a new one has been provided
            if new_password:
                hashed_password = encrypt_password(new_password)
                cursor.execute("UPDATE secureusers SET password = %s WHERE username = %s", (hashed_password, username))

            cursor.execute("UPDATE secureusers SET name = %s, email = %s, phone_number = %s WHERE username = %s", (name, email, phone_number, username))
            if address:
                cursor.execute("UPDATE customer SET address = %s WHERE user_id = (SELECT user_id FROM secureusers WHERE username = %s)", (address, username))

            flash('Profile successfully updated.')
            return redirect(url_for('profile'))

    else:
        return redirect(url_for('login'))


@app.route('/updateprofile-password', methods=["GET", "POST"])
def updateprofile_password():
    if 'loggedin' in session:
        username = session['username']
        cursor = getCursor(dictionary_cursor=True)
        
        if request.method == 'POST':
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # Check if the new password and confirmation password match
            if new_password != confirm_password:
                flash("New password and confirmation password do not match.", "error")
                return redirect(url_for('updateprofile_password'))

            # Hash the new password
            hashed_password = encrypt_password(new_password)

            # Update the password in the database
            cursor.execute("UPDATE secureusers SET password = %s WHERE username = %s", (hashed_password, username))

            flash('Password successfully updated.')
            return redirect(url_for('profile'))

        elif request.method == 'GET':
            # If the request is a GET, simply render the update profile password page
            return render_template('updateprofile-password.html')  
    else:
        return redirect(url_for('login'))

        






if __name__ == '__main__':
    app.run(debug=True)