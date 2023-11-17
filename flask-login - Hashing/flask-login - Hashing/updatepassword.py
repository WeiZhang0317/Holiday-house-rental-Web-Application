import bcrypt
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import Flask

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'holiday_house_rental_system'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)
with app.app_context():
    
    # Hash all existing passwords in the database

    def get_all_users():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM secureusers") 
        users = cursor.fetchall()
        return users

    def update_hashed_password(user_id, hashed_pw):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE secureusers SET password = %s WHERE user_id = %s", (hashed_pw, user_id))
        mysql.connection.commit()

    users = get_all_users()
    for user in users:
        user_id = user['user_id']
        plain_password = user['password']
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        update_hashed_password(user_id, hashed_pw.decode('utf-8'))

if __name__ == '__main__':
    app.run(debug=True)