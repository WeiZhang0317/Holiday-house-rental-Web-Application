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


# Connect to the MySQL database with credentials and details from the 'connect' module
# Create and return a cursor object from the database connection
# If dictionary_cursor is True, the cursor returns query results as dictionaries
def getCursor(dictionary_cursor=False):
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, password=connect.dbpass, host=connect.dbhost, database=connect.dbname, autocommit=True)
    cursor = connection.cursor(dictionary=dictionary_cursor)
    return cursor

# encrypt plain password
def encrypt_password(plain_password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')

# encrypt the password in database securedata
def encrypt_all_user_passwords():
    cursor = getCursor()
    cursor.execute("SELECT * FROM secureusers")
    users = cursor.fetchall()

    for user in users:
        user_id = user[0]
        plain_password = user[4]

 #make sure the encrypted password does not need to be encrypted again       
        if not plain_password.startswith('$2b$'):
            hashed_pw = encrypt_password(plain_password)
            cursor.execute("UPDATE secureusers SET password = %s WHERE user_id = %s", (hashed_pw, user_id))


#Differentiate logged-in user types and navigate to different homepages
def get_home_url_by_role():
    role_name = session.get('role_name')
    if role_name == 'customer':
        return url_for('home')
    elif role_name == 'staff':
        return url_for('staffhome')
    elif role_name == 'staff-admin':
        return url_for('staffhome')


    
encrypt_all_user_passwords()

# This section of code defines the main route for the application. 
# It first checks if the user is already logged in by examining the session. 
# Depending on the user's role, identified as either 'customer' or 'staff', 
# the user is redirected to the appropriate home page.

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


# route for customer register only
#It checks if a username exists, validates user inputs like email and password, 
# and inserts new user details into the database if validations pass.

@app.route('/register', methods=['GET', 'POST'])
def register():
    form_data = {}
    msg = ''
    cursor = getCursor(dictionary_cursor=True)

#get the information the user filled when they submit the form
    if request.method == 'POST':
        form_data = request.form.to_dict()

        name = form_data.get('name')
        username = form_data.get('username')
        password = form_data.get('password')
        phone_number = form_data.get('phone_number')
        email = form_data.get('email')
        address = form_data.get('address')


     # validate the information users filled

        cursor.execute('SELECT * FROM secureusers WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        #check if the user name is used
        if account:
            msg = 'Account already exists! Please choose another user name'
        
         #check email format
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address! Use format: username@example.com'
        
        #check if the info has been filled
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
 
        #check if the name is only contains letter and space
        elif not name or not re.match(r'^[A-Za-z\s]+$', name):
           msg = 'Invalid name! Name should only contain letters and spaces.' 
 
        #check if customer has filled the address
        elif not address:
           msg = 'Please enter your address!' 

        #check if passwrod length is at least 4   
        elif len(password) < 4:
           msg = 'Password must have at least 4 characters.'
        else:
        
        # if the varify has been passed,
        #the password will be encrpted and all the data will be update to the database
        # flash messgae to let customer knows that they have been registered
        # reder the html template
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('INSERT INTO secureusers (username, name, email, phone_number, password, role_name) VALUES (%s, %s, %s, %s, %s, %s)', (username, name, email, phone_number, hashed_password, 'customer'))
            cursor.execute('SELECT user_id FROM secureusers WHERE username = %s', (username,))
            user_id = cursor.fetchone()['user_id']
            cursor.execute('INSERT INTO customer (address, user_id) VALUES (%s, %s)', (address, user_id))
            msg = 'You have successfully registered!' 
            return render_template('register.html', form_data=form_data,msg=msg)

        return render_template('register.html', form_data=form_data, msg=msg)
# if it is the get request, render template and shows empty form
    else:
        return render_template('register.html',form_data=form_data, msg=msg)

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

        search_query = request.args.get('search')  # get search keywords
        if search_query is not None:
    
           cursor.execute("SELECT * FROM holiday_houses WHERE house_address LIKE %s", ('%' + search_query + '%',))
        else:
      
           cursor.execute('SELECT * FROM holiday_houses')

        holiday_houses = cursor.fetchall()

        # Render the home template with account, username, and holiday houses data
        return render_template('home.html', account=account, username=username, holiday_houses=holiday_houses)
    
    # User is not logged in, redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/home - this will be the home page, only accessible for loggedin staff/admin
#on this page it shows house photo and infomation, including the add, edit and delete button
# it also include the search bar
@app.route('/staffhome')
def staffhome():
    cursor = getCursor(dictionary_cursor=True)
    # Check if user is logged in
    if 'loggedin' in session and (session.get('role_name') == 'staff' or session.get('role_name') == 'staff-admin'):

        # User is logged in, show them the home page
        username = session['username']
        cursor.execute('SELECT * FROM secureusers WHERE username = %s', (username,))
        account = cursor.fetchone()

        search_query = request.args.get('search')  # get search keywords
        if search_query is not None:
        
           cursor.execute("SELECT * FROM holiday_houses WHERE house_address LIKE %s", ('%' + search_query + '%',))
        else:
        # show all houses 
           cursor.execute('SELECT * FROM holiday_houses')

        holiday_houses = cursor.fetchall()

        # Render the home template with account, username, and holiday houses data
        return render_template('staffhome.html', account=account, username=username, holiday_houses=holiday_houses)
    
    # User is not logged in, redirect to login page
    return redirect(url_for('login'))





# this is the function for staff(include admin) to add house 
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


            flash('New holiday house added successfully!','house')
            return redirect(url_for('staffhome'))

        
        return render_template('staffhome-add.html',home_url=home_url)

    return redirect(url_for('login'))



# this is the function for staff(include admin) to edit house 
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

            update_query = '''
            UPDATE holiday_houses 
            SET house_address = %s, number_of_bedrooms = %s, number_of_bathrooms = %s, 
                maximum_occupancy = %s, rental_per_night = %s
            '''
            update_values = (house_address, number_of_bedrooms, number_of_bathrooms, maximum_occupancy, rental_per_night)

            if filename:
                update_query += ', house_image = %s'
                update_values += (filename,)
            else:
                # If no new image is uploaded, don't update the house_image field
                cursor.execute('SELECT house_image FROM holiday_houses WHERE house_id = %s', (house_id,))
                current_image = cursor.fetchone()
                if current_image and current_image['house_image']:
                    filename = current_image['house_image']

            update_query += ' WHERE house_id = %s'
            update_values += (house_id,)

            cursor.execute(update_query, update_values)
            flash('House updated successfully!', 'house')
            return redirect(url_for('staffhome'))


        else:
            # For a GET request, retrieve the current house data and display it in the form
            cursor.execute('SELECT * FROM holiday_houses WHERE house_id = %s', (house_id,))
            house = cursor.fetchone()
            return render_template('staffhome-edit.html', house=house, home_url=home_url)

    else:
        return redirect(url_for('login'))


# this is the function for staff(include admin) to delete house on the staffhome page
@app.route('/delete_house/<int:house_id>')
def delete_house(house_id):
    cursor = getCursor(dictionary_cursor=True)

    # check if user is staff or admin
    if 'loggedin' in session and (session.get('role_name') == 'staff' or session.get('role_name') == 'staff-admin'):
        # execute delete
        cursor.execute('DELETE FROM holiday_houses WHERE house_id = %s', (house_id,))
        flash('Holiday house deleted successfully!','house')

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

#update the profile for all the users
@app.route('/update_profile', methods=["GET", "POST"])
def update_profile():
    if 'loggedin' in session:
        username = session['username']
        cursor = getCursor(dictionary_cursor=True)
        home_url = get_home_url_by_role() 

 #When the user navigates to the profile update page.
#It queries the secureusers table for basic user information and the customer table for the user's address. 
#This data is then passed to the updateprofile.html template to pre-fill the form with the user's existing information.  
        if request.method == 'GET':
            cursor.execute('SELECT * FROM secureusers WHERE username = %s', (username,))
            account = cursor.fetchone()
            cursor.execute('SELECT c.address FROM secureusers AS s JOIN customer AS c ON s.user_id=c.user_id WHERE s.username = %s', (username,))
            customer = cursor.fetchone()

            return render_template('updateprofile.html', account=account, customer=customer,home_url=home_url)

        elif request.method == 'POST':
            name = request.form.get('name')
            new_username = request.form.get('username') 
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            
            address = request.form.get('address')

             # Check name format (only letters and spaces)
            if not re.match(r'^[A-Za-z\s]+$', name):
                flash('Invalid name! Name should only contain letters and spaces.')
                return redirect(url_for('update_profile'))
            
            # Validation: Check if the new username already exists in the database, excluding the current user
            if new_username and new_username != username:
                cursor.execute('SELECT * FROM secureusers WHERE username = %s AND username != %s', (new_username, username))
                account = cursor.fetchone()
                if account:
                    flash('Username already exists! Please choose another.')
                    return redirect(url_for('update_profile'))

            # Update user details in the database
            cursor.execute("UPDATE secureusers SET name = %s, email = %s, phone_number = %s WHERE username = %s", (name, email, phone_number, username))
          
          
        
            if address:
                cursor.execute("UPDATE customer SET address = %s WHERE user_id = (SELECT user_id FROM secureusers WHERE username = %s)", (address, username))

            if new_username and new_username != username:
                cursor.execute("UPDATE secureusers SET username = %s WHERE username = %s", (new_username, username))
                session['username'] = new_username 
                
            flash('Profile successfully updated.')
            return redirect(url_for('profile'))

    else:
        return redirect(url_for('login'))


# This is for a Flask web application's password update feature.




# Users not logged in are redirected to the login page.
@app.route('/updateprofile-password', methods=["GET", "POST"])
def updateprofile_password():
    home_url = get_home_url_by_role() 
    if 'loggedin' in session:
        username = session['username']
        cursor = getCursor(dictionary_cursor=True)

# On a POST request, it checks if the new password matches the confirmation         
        if request.method == 'POST':
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # Check if the new password and confirmation password match
            if new_password != confirm_password:
                flash("New password and confirmation password do not match.", "error")
                return redirect(url_for('updateprofile_password'))
            
            # Validate the password length,is at least 4 characters long.
            if len(new_password) < 4:
                flash("Password must have at least 4 characters.", "error")
                return redirect(url_for('updateprofile_password'))

           #If valid, the password is encrypted and updated in the database, and the user is redirected to their profile.   
            # Hash the new password
            hashed_password = encrypt_password(new_password)

            # Update the password in the database
            cursor.execute("UPDATE secureusers SET password = %s WHERE username = %s", (hashed_password, username))

            flash('Password successfully updated.')
            return redirect(url_for('profile'))
      # When accessed via GET, it displays the password update form.
        elif request.method == 'GET':
            # If the request is a GET, simply render the update profile password page
            return render_template('updateprofile-password.html',home_url=home_url)  
    else:
        return redirect(url_for('login'))

 #This code for a web application allows staff members (not include admin) to view customer details. 
 
 # The results are displayed on the viewcustomer.html page. 

@app.route('/viewcustomer')
def viewcustomer():

#If a staff member is logged in, they can either view all customers 
# or search for specific ones by username or name.     
    if 'loggedin' in session and session.get('role_name') == 'staff':
        cursor = getCursor(dictionary_cursor=True)
        search_query = request.args.get('search')  

        if search_query:
            
            query = """
                SELECT s.*, c.customer_number, c.address
                FROM secureusers s
                JOIN customer c ON s.user_id = c.user_id
                WHERE role_name='customer' AND (s.username LIKE %s OR s.name LIKE %s )
            """
            search_term = '%' + search_query + '%'
            cursor.execute(query, (search_term, search_term))
        else:
           
            cursor.execute("SELECT s.*, c.customer_number, c.address FROM secureusers s JOIN customer c ON s.user_id = c.user_id where role_name='customer'")
        
        customers = cursor.fetchall()
        home_url = get_home_url_by_role()  
          # Render the viewcustomer page with the customers list, home URL, and any search query
        return render_template('viewcustomer.html', customers=customers, home_url=home_url, search_query=search_query)

    else:
        return redirect(url_for('login'))

# This is the function for the admin to manage customer
# it inlude customer information page,
#search bar and also the add, edit and delete button
@app.route('/editcustomer')
def editcustomer():
    
    if 'loggedin' in session and session.get('role_name') == 'staff-admin':
        cursor = getCursor(dictionary_cursor=True)
        #the search function to search customer
        search_query = request.args.get('search')  
        # get search keywords

        if search_query:
            # Search for customers matching the search query
            query = """
                SELECT s.*, c.address, c.customer_number
                FROM secureusers s
                JOIN customer c ON s.user_id = c.user_id
                WHERE role_name='customer' AND (s.username LIKE %s OR s.name LIKE %s )
            """
            search_term = '%' + search_query + '%'
            cursor.execute(query, (search_term, search_term))
        else:
            # Show all customers
           cursor.execute("SELECT s.*, c.address, c.customer_number FROM secureusers s JOIN customer c ON s.user_id = c.user_id where role_name='customer'")
        customers = cursor.fetchall()  
        home_url = get_home_url_by_role()  
        return render_template('editcustomer.html', customers=customers,home_url=home_url, search_query=search_query)

    else:
        #if not log in back to the login page
        return redirect(url_for('login'))
    
#this is the form to edit the customer 
@app.route('/edit_customer_page/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer_page(customer_id):

    #check if the login is admin
    if 'loggedin' in session and session.get('role_name') == 'staff-admin':
        cursor = getCursor(dictionary_cursor=True)
     
     #For a GET request, fetch the specified customer's details from the database
        if request.method == 'GET':
            cursor.execute('SELECT s.*, c.address, c.customer_number FROM secureusers s JOIN customer c ON s.user_id = c.user_id WHERE s.role_name = %s AND s.user_id = %s', ('customer', customer_id))
            customer = cursor.fetchone()
            home_url = get_home_url_by_role() 
      # Render the edit_customer_page template with the fetched customer details and home URL       
            return render_template('edit_customer_page.html', customer=customer,home_url=home_url)
        elif request.method == 'POST':
        # For a POST request, retrieve form data for customer update     
            username = request.form.get('username')
            name = request.form.get('name')
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            address = request.form.get('address')
            customer_number = request.form.get('customer_number')
        # Initialize an error message variable for future use
            error_msg = None

            # Check name format (only letters and spaces)
            if not re.match(r'^[A-Za-z\s]+$', name):
                error_msg = 'Invalid name! Name should only contain letters and spaces.'
            
            
            # Check if the username already exists in the database for another user
            cursor.execute('SELECT user_id FROM secureusers WHERE username = %s AND user_id != %s', (username, customer_id))
            if cursor.fetchone():
                flash('Username already taken. Please choose another username.')
                return redirect(url_for('edit_customer_page', customer_id=customer_id))

            # If there's an error, return to the form with the error message
            if error_msg:
                flash(error_msg)
                return redirect(url_for('edit_customer_page', customer_id=customer_id))
            
            
            # Update the database records if validation passes
            cursor.execute('UPDATE secureusers SET username = %s, name = %s, email = %s, phone_number = %s WHERE user_id = %s',
                           (username, name, email, phone_number, customer_id))
            cursor.execute('UPDATE customer SET customer_number=%s, address = %s WHERE user_id = %s',
                           (customer_number,address, customer_id))
            flash('Customer editted successfully! ','delete,edit,add')
            return redirect(url_for('editcustomer'))           

    else:
        #if not log in back to the login page
        return redirect(url_for('login'))    

  
    
# the form for admin to add a new customer
@app.route('/edit_customer_add', methods=['GET', 'POST'])
def edit_customer_add():
    # Check if the user is logged in and has the 'staff-admin' role  
    if 'loggedin' in session and session.get('role_name') == 'staff-admin':
        cursor = getCursor(dictionary_cursor=True)
        form_data = {}
   # Retrieve form data and initialize variables
        if request.method == 'POST':
            form_data = request.form.to_dict()

            username = form_data.get('username')
            name = form_data.get('name')
            email = form_data.get('email')
            phone_number = form_data.get('phone_number')
            address = form_data.get('address')
            customernumber = form_data.get('customernumber')
            encrypted_password = encrypt_password('123456')

            # Check if the username already exists
            cursor.execute('SELECT * FROM secureusers WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                flash('Username already exists! Please choose another.')
                return render_template('edit_customer_add.html', form_data=form_data, home_url=get_home_url_by_role())

            # Check name format (only letters and spaces)
            if not re.match(r'^[A-Za-z\s]+$', name):
                flash('Invalid name! Name should only contain letters and spaces.')
                return render_template('edit_customer_add.html', form_data=form_data, home_url=get_home_url_by_role())

            # Insert into secureusers and customer
            cursor.execute('INSERT INTO secureusers (username, name, email, phone_number, password, role_name) VALUES (%s, %s, %s, %s, %s, %s)', (username, name, email, phone_number, encrypted_password, 'customer'))
           
            cursor.execute('SELECT user_id FROM secureusers WHERE username = %s', (username,))
            user_id = cursor.fetchone()['user_id'] 
            cursor.execute('INSERT INTO customer (customer_number, address, user_id) VALUES (%s, %s, %s)', (customernumber, address, user_id))
            
            flash('New customer added successfully! The default password is 123456, please contact user to update their password.', 'delete,edit,add')

            return redirect(url_for('editcustomer'))

        else:
            # Render the add customer form for GET request
            home_url = get_home_url_by_role() 
            return render_template('edit_customer_add.html', home_url=home_url, form_data=form_data)

    else:
         # Redirect non-staff-admin users to the login page
        return redirect(url_for('login'))

#delete customer from edit customer page
@app.route('/delete_customer/<int:customer_id>')
def delete_customer(customer_id):
     # Initialize a database cursor with dictionary style results
    cursor = getCursor(dictionary_cursor=True)
    
     # Check if user is logged in and has the 'staff-admin' role
    if 'loggedin' in session and session.get('role_name') == 'staff-admin':
        try:
           #delete from the child tabble customer
            cursor.execute('DELETE FROM customer WHERE user_id = %s', (customer_id,))

            # delete from the parent table secureusers 
            cursor.execute('DELETE FROM secureusers WHERE user_id = %s', (customer_id,))

            flash('Customer deleted successfully!','delete,edit,add')
        except mysql.connector.Error as err:
            flash(f'Error occurred: {err}', 'error')
        finally:
            cursor.close()
       # Redirect to the 'editcustomer' page
        return redirect(url_for('editcustomer'))

    else:
         # Redirect to the login page if user is not logged in or not an admin
        return redirect(url_for('login'))

#page for admin to manage staff, including add, edit and delete button
@app.route('/editstaff')
def editstaff():
    # Check if the user is logged in and has the 'staff-admin' role
    if 'loggedin' in session and session.get('role_name') == 'staff-admin':
         # Initialize a database cursor with dictionary style results
        cursor = getCursor(dictionary_cursor=True)
        
        # Execute SQL query to select staff details from 'secureusers' and 'staff' tables
        cursor.execute("SELECT s.*, staff.date_joined,staff.staff_number FROM secureusers s JOIN staff ON s.user_id = staff.user_id ")
        staffs = cursor.fetchall()
        # Get the home URL based on the user role  
        home_url = get_home_url_by_role()  
        return render_template('editstaff.html', staffs=staffs,home_url=home_url)

    else:
        # Redirect to the login page if user is not logged in or not an admin
        return redirect(url_for('login'))
    
 
#page for admin to edit staff information
@app.route('/edit_staff_page/<int:staff_id>', methods=['GET', 'POST'])
def edit_staff_page(staff_id):

    # Check if the user is logged in and has the 'staff-admin' role
    if 'loggedin' in session and session.get('role_name') == 'staff-admin':
        cursor = getCursor(dictionary_cursor=True)
        # Handle GET request: Fetch and display staff details for editing
        if request.method == 'GET':
            cursor.execute("SELECT s.*, staff.staff_number, staff.date_joined FROM secureusers s JOIN staff ON s.user_id = staff.user_id  WHERE  s.user_id = %s", (staff_id,))
              # Fetch the staff member's data
            staff = cursor.fetchone()
            home_url = get_home_url_by_role()
            return render_template('edit_staff_page.html', staff=staff,home_url=home_url)
     # Handle POST request: Update staff details
     
        elif request.method == 'POST':
            username = request.form.get('username')
            name = request.form.get('name')
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            date_joined = request.form.get('date_joined')
            staff_number = request.form.get('staff_number')
            role_name = request.form.get('role_name')


            # Validation : Additional format checks
            error_msg = None

            # Check name format (only letters and spaces)
            if not re.match(r'^[A-Za-z\s]+$', name):
                error_msg = 'Invalid name! Name should only contain letters and spaces.'

            # Check if the username already exists in the database for another staff
            cursor.execute('SELECT user_id FROM secureusers WHERE username = %s AND user_id != %s', (username, staff_id))
            if cursor.fetchone():
                flash('Username already taken. Please choose another username.', 'error')
                return redirect(url_for('edit_staff_page', staff_id=staff_id))
    

            # If there's an error, return to the form with the error message
            if error_msg:
                flash(error_msg)
                return redirect(url_for('edit_customer_add'))
            
          #update database and flash info
            cursor.execute('UPDATE secureusers SET username = %s, name = %s, email = %s, phone_number = %s,  role_name =%s WHERE user_id = %s',
                           (username, name, email, phone_number, role_name, staff_id))
            cursor.execute('UPDATE staff SET date_joined = %s, staff_number=%s WHERE user_id = %s',
                           (date_joined,staff_number, staff_id))
            flash('Staff editted successfully! ','staff')
            return redirect(url_for('editstaff'))           

    else:
        return redirect(url_for('login'))    

 #page for admin to add staff information 
@app.route('/edit_staff_add', methods=['GET', 'POST'])
def edit_staff_add():

    # Check if the user is logged in and has the 'staff-admin' role
    if 'loggedin' in session and session.get('role_name') == 'staff-admin':
        cursor = getCursor(dictionary_cursor=True)
        form_data = {}

        if request.method == 'POST':
             # Convert the form data from the request to a dictionary
            form_data = request.form.to_dict()

            try:
                 # Extract individual pieces of data from the form
                username = form_data['username']
                name = form_data['name']
                email = form_data['email']
                phone_number = form_data['phone_number']
                date_joined = form_data['date_joined']
                staff_number = form_data['staff_number']
                role_name = form_data['role_name']

                # Encrypt a predefined password ('56789' in this case) and store it
                encrypted_password = encrypt_password('56789')

                # Check if the username already exists
                cursor.execute('SELECT * FROM secureusers WHERE username = %s', (username,))
                account = cursor.fetchone()
                if account:
                    flash('Username already exists! Please choose another.')
                    return render_template('edit_staff_add.html', form_data=form_data)

                # Check name format (only letters and spaces)
                if not re.match(r'^[A-Za-z\s]+$', name):
                    flash('Invalid name! Name should only contain letters and spaces.')
                    return render_template('edit_staff_add.html', form_data=form_data)

                # Insert into secureusers
                cursor.execute('INSERT INTO secureusers (username, name, email, phone_number, password, role_name) VALUES (%s, %s, %s, %s, %s, %s)', (username, name, email, phone_number, encrypted_password, role_name))

                # Get user_id
                cursor.execute('SELECT user_id FROM secureusers WHERE username = %s', (username,))
                user_id = cursor.fetchone()['user_id']

                # Insert into staff
                cursor.execute('INSERT INTO staff (staff_number, date_joined, user_id) VALUES (%s, %s, %s)', (staff_number, date_joined, user_id))

                flash('New staff added successfully! The default password is 56789, please contact user to update their password.', 'staff')
          # Handling exceptions that might occur during form data processing or database operations
            except Exception as e:
                print("An error occurred:", e)
                flash('An error occurred while adding staff.', 'error')
         # Finally block to ensure certain actions are executed regardless of exceptions
            finally:
                if cursor:
                    cursor.close()

            return redirect(url_for('editstaff'))
       # If the request method is not POST (it is GET)
        else:
            home_url = get_home_url_by_role() 
            return render_template('edit_staff_add.html', home_url=home_url, form_data=form_data)

    else:
        return redirect(url_for('login'))

#function for admin to delete staff
@app.route('/delete_staff/<int:staff_id>')
def delete_staff(staff_id):
    # Initialize a database cursor with dictionary style results
    cursor = getCursor(dictionary_cursor=True)

    # Check if the user is logged in and has the 'staff-admin' role
    if 'loggedin' in session and session.get('role_name') == 'staff-admin':
        try:
            # Delete the staff member record from the 'staff' table (child table)
            cursor.execute('DELETE FROM staff WHERE user_id = %s', (staff_id,))

            # Delete the associated user record from the 'secureusers' table (parent table)
            cursor.execute('DELETE FROM secureusers WHERE user_id = %s', (staff_id,))

            # Display a success message to the user
            flash('Staff deleted successfully!', 'staff')
        except mysql.connector.Error as err:
            # Display an error message if an exception occurs
            flash(f'Error occurred: {err}', 'error')
        finally:
            # Close the database cursor to free up resources
            cursor.close()

        # Redirect to the 'editstaff' page after deletion
        return redirect(url_for('editstaff'))

    else:
        # Redirect to the login page if user is not logged in or not an admin
        return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)