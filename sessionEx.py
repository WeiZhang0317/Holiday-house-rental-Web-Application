from flask import Flask, session, redirect, url_for, request

app = Flask(__name__)

# Set a secret key for the session. Make sure to keep this secure in a real application.
app.secret_key = 'your_secret_key'

def is_authenticated():
    return 'username' in session

def get_user_role():
    # In a real application, you would likely retrieve the user's role from a database.
    # For this example, let's assume a user with the username 'admin' has the role 'admin'.
    if 'username' in session:
        if session['username'] == 'admin':
            return 'admin'
        elif session['username'] == 'member':
            return 'member'
        elif session['username'] == 'staff':
            return 'staff'
    return None

@app.route('/')
def index():
    # Check if the user is authenticated. If yes, display a personalized greeting.
    if is_authenticated():
        return f"Hello, {session['username']}! <a href='/logout'>Logout</a>"

    return "Hello, stranger!<p> <a href='/login'>Login</a>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Assuming the user submits the form with a field named 'username'
        username = request.form['username']

        # Store the 'username' in the session.
        session['username'] = username
        return redirect(url_for('index'))

    return '''
        <form method="post">
            <p><input type="text" name="username" placeholder="Enter your username"></p>
            <p><input type="submit" value="Login"></p>
        </form>
    '''

@app.route('/logout')
def logout():
    # Clear the session to log the user out.
    session.clear()
    return redirect(url_for('index'))

@app.route('/protected')
def protected():
    # Check if the user is authenticated. If not, redirect to the login page.
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()

    # Check if the user's role is allowed to access this page.
    if user_role in ['admin', 'member', 'staff']:
        return f"This is a protected page for {user_role}, {session['username']}! <a href='/logout'>Logout</a>"
    else:
        return "Unauthorized"

@app.route('/admin')
def admin():
    # Check if the user is authenticated. If not, redirect to the login page.
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()

    # Check if the user's role is allowed to access this page.
    if user_role == 'admin':
        return "Welcome, Admin! <a href='/logout'>Logout</a>"
    else:
        return "Unauthorized"

@app.route('/member')
def member():
    # Check if the user is authenticated. If not, redirect to the login page.
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()

    # Check if the user's role is allowed to access this page.
    if user_role in ['admin', 'member']:
        return f"Welcome, Member! {session['username']}! <a href='/logout'>Logout</a>"
    else:
        return "Unauthorized"

@app.route('/staff')
def staff():
    # Check if the user is authenticated. If not, redirect to the login page.
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()

    # Check if the user's role is allowed to access this page.
    if user_role in ['admin', 'staff']:
        return f"Welcome, Staff! {session['username']}! <a href='/logout'>Logout</a>"
    else:
        return "Unauthorized"

if __name__ == '__main__':
    app.run(debug=True)
