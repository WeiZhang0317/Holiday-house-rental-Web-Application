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


def get_home_url_by_role():
    role_name = session.get('role_name')
    if role_name == 'customer':
        return url_for('home')
    elif role_name == 'staff':
        return url_for('staffhome')
    elif role_name == 'staff-admin':
        return url_for('staffhome')


    
encrypt_all_user_passwords()

# http://localhost:5000/ - main page
@app.route('/')
def main():
    # check if user has loggin 
    if 'loggedin' in session and session.get('role_name') == 'customer':
        # if user already login it goes to home page
        return redirect(url_for('home'))
    elif 'loggedin' in session and session.get('role_name') == 'staff':
        return redirect(url_for('staffhome'))
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
                   return redirect(url_for('staffhome'))
                elif account['role_name'] == 'staff':
                   return redirect(url_for('staffhome'))
                else:
                    return redirect(url_for('home'))
            else:
                #password incorrect
                msg = 'Incorrect password!'
        else:
            # Account doesnt exist or username incorrect
            msg = 'Incorrect username'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

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
    
    #only staff or admin are able to add house
    if 'loggedin' in session and (session.get('role_name') == 'staff' or session.get('role_name') == 'staff-admin'):
        home_url=get_home_url_by_role()
        # when click submit button it reuqest info from html 
        if request.method == 'POST':
            house_address = request.form['house_address']
            number_of_bedrooms = request.form['number_of_bedrooms']
            number_of_bathrooms = request.form['number_of_bathrooms']
            maximum_occupancy = request.form['maximum_occupancy']
            rental_per_night= request.form['rental_per_night']
            
            #check if there is file called house_image
            if 'house_image' in request.files:
                house_image = request.files['house_image']

                #make sure does not upload empty file
                if house_image.filename != '':
                    #make sure the file name is safe
                    filename = secure_filename(house_image.filename)
                    #file is going to be saved under static
                    house_image.save(os.path.join('static', filename))
                   
        
           #update database
            cursor.execute('INSERT INTO holiday_houses (house_address, number_of_bedrooms, number_of_bathrooms, maximum_occupancy, rental_per_night, house_image) VALUES (%s, %s, %s, %s, %s, %s)', 
               (house_address, number_of_bedrooms, number_of_bathrooms, maximum_occupancy, rental_per_night, filename))


            flash('New holiday house added successfully!')
            return redirect(url_for('staffhome'))

        
        return render_template('staffhome-add.html',home_url=home_url)

    return redirect(url_for('login'))


@app.route('/edit_house/<int:house_id>', methods=['GET', 'POST'])
def edit_house(house_id):
    cursor = getCursor(dictionary_cursor=True)

    if 'loggedin' in session and (session.get('role_name') == 'staff' or session.get('role_name') == 'staff-admin'):
        home_url=get_home_url_by_role()
        if request.method == 'POST':
            # Extract the data from the form submission
            house_address = request.form['house_address']
            number_of_bedrooms = request.form['number_of_bedrooms']
            number_of_bathrooms = request.form['number_of_bathrooms']
            maximum_occupancy = request.form['maximum_occupancy']
            rental_per_night = request.form['rental_per_night']

            # Assuming 'house_image' is optional
            if 'house_image' in request.files and request.files['house_image'].filename != '':
                house_image = request.files['house_image']
                filename = secure_filename(house_image.filename)
                house_image.save(os.path.join('static', filename))
            else:
                filename = None

            # Update the house in the database
            update_query = '''
            UPDATE holiday_houses 
            SET house_address = %s, number_of_bedrooms = %s, number_of_bathrooms = %s, 
                maximum_occupancy = %s, rental_per_night = %s
            '''
            update_values = (house_address, number_of_bedrooms, number_of_bathrooms, maximum_occupancy, rental_per_night)

            if filename:
                update_query += ', house_image = %s'
                update_values += (filename,)

            update_query += ' WHERE house_id = %s'
            update_values += (house_id,)

            cursor.execute(update_query, update_values)

            flash('House updated successfully!')
            return redirect(url_for('staffhome'))

        else:
            # For a GET request, retrieve the current house data and display it in the form
            cursor.execute('SELECT * FROM holiday_houses WHERE house_id = %s', (house_id,))
            house = cursor.fetchone()
            return render_template('staffhome-edit.html', house=house, home_url=home_url)

    else:
        return redirect(url_for('login'))



@app.route('/delete_house/<int:house_id>')
def delete_house(house_id):
    cursor = getCursor(dictionary_cursor=True)

    # check if user is staff or admin
    if 'loggedin' in session and (session.get('role_name') == 'staff' or session.get('role_name') == 'staff-admin'):
        # execute delete
        cursor.execute('DELETE FROM holiday_houses WHERE house_id = %s', (house_id,))
        flash('Holiday house deleted successfully!')

        return redirect(url_for('staffhome'))

    else:
        #if not login return to login page
        return redirect(url_for('login'))





# The profile function is for all of the users, as they are logged in, customers, staff and admin all can view their profile and edit it
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
        cursor.execute('SELECT s.username,staff.staff_number,staff.date_joined FROM staff JOIN secureusers AS s ON staff.user_id=s.user_id  WHERE s.username = %s', (username,))
        staff = cursor.fetchone()
        home_url = get_home_url_by_role()  

        return render_template('profile.html', account=account, username=username, customer=customer,staff=staff, home_url=home_url )
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/update_profile', methods=["GET", "POST"])
def update_profile():
    if 'loggedin' in session:
        username = session['username']
        cursor = getCursor(dictionary_cursor=True)
        home_url = get_home_url_by_role()  
        if request.method == 'GET':
            cursor.execute('SELECT * FROM secureusers WHERE username = %s', (username,))
            account = cursor.fetchone()
            cursor.execute('SELECT c.address FROM secureusers AS s JOIN customer AS c ON s.user_id=c.user_id WHERE s.username = %s', (username,))
            customer = cursor.fetchone()
            return render_template('updateprofile.html', account=account, customer=customer,home_url=home_url)

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
    home_url = get_home_url_by_role() 
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
            return render_template('updateprofile-password.html',home_url=home_url)  
    else:
        return redirect(url_for('login'))

        

@app.route('/viewcustomer')
def viewcustomer():
    
    if 'loggedin' in session and session.get('role_name') == 'staff':
        cursor = getCursor(dictionary_cursor=True)
        
        
        cursor.execute("SELECT s.*, c.address FROM secureusers s JOIN customer c ON s.user_id = c.user_id where role_name='customer'")
        customers = cursor.fetchall()  
        home_url = get_home_url_by_role()  
        return render_template('viewcustomer.html', customers=customers,home_url=home_url)

    else:
        return redirect(url_for('login'))

@app.route('/editcustomer')
def editcustomer():
    
    if 'loggedin' in session and session.get('role_name') == 'staff-admin':
        cursor = getCursor(dictionary_cursor=True)
        
        
        cursor.execute("SELECT s.*, c.address FROM secureusers s JOIN customer c ON s.user_id = c.user_id where role_name='customer'")
        customers = cursor.fetchall()  
        home_url = get_home_url_by_role()  
        return render_template('editcustomer.html', customers=customers,home_url=home_url)

    else:
        return redirect(url_for('login'))
    

@app.route('/edit_customer_page/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer_page(customer_id):
    if 'loggedin' in session and session.get('role_name') == 'staff-admin':
        cursor = getCursor(dictionary_cursor=True)
        if request.method == 'GET':
            cursor.execute('SELECT s.*, c.address FROM secureusers s JOIN customer c ON s.user_id = c.user_id WHERE s.role_name = %s AND s.user_id = %s', ('customer', customer_id))
            customer = cursor.fetchone()
            home_url = get_home_url_by_role() 
            return render_template('edit_customer_page.html', customer=customer,home_url=home_url)
        elif request.method == 'POST':
            username = request.form.get('username')
            name = request.form.get('name')
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            address = request.form.get('address')

            cursor.execute('UPDATE secureusers SET username = %s, name = %s, email = %s, phone_number = %s WHERE user_id = %s',
                           (username, name, email, phone_number, customer_id))
            cursor.execute('UPDATE customer SET address = %s WHERE user_id = %s',
                           (address, customer_id))

            return redirect(url_for('editcustomer'))           

    else:
        return redirect(url_for('login'))    
    

@app.route('/edit_customer_add', methods=['GET', 'POST'])
def edit_customer_add():
   
    
    #only staff or admin are able to add house
    if 'loggedin' in session and  session.get('role_name') == 'staff-admin':
        cursor = getCursor(dictionary_cursor=True)
        if request.method == 'GET':
            home_url = get_home_url_by_role() 
            return render_template('edit_customer_add.html', home_url=home_url)
        elif request.method == 'POST':
            username = request.form.get('username')
            name = request.form.get('name')
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            address = request.form.get('address')
            customernumber = request.form.get('customernumber')

            encrypted_password = encrypt_password('123456') 
        

        
            cursor.execute ('INSERT INTO secureusers (username, name, email, phone_number, password, role_name) VALUES (%s, %s, %s, %s, %s, %s)', (username, name, email, phone_number, encrypted_password, 'customer'))
           
            cursor.execute('SELECT user_id FROM secureusers WHERE username = %s', (username,))
            user_id = cursor.fetchone()['user_id']  # 获取 user_id
            cursor.execute('INSERT INTO customer (customer_number, address, user_id) VALUES (%s, %s, %s)', (customernumber, address, user_id))
            flash('New customer added successfully! The default customer password is 123456')




            return redirect(url_for('edit_customer_add'))           

    else:
        return redirect(url_for('login'))    
    





@app.route('/delete_customer/<int:customer_id>')
def delete_customer(customer_id):
    cursor = getCursor(dictionary_cursor=True)

    # check if user is staff or admin
    if 'loggedin' in session and session.get('role_name') == 'staff-admin':
        # execute delete
        cursor.execute('DELETE FROM secureusers WHERE user_id = %s', (customer_id,))
        cursor.execute('DELETE FROM customer WHERE user_id = %s', (customer_id,))
        flash('Customer deleted successfully!')

        return redirect(url_for('editcustomer'))

    else:
        #if not login return to login page
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)