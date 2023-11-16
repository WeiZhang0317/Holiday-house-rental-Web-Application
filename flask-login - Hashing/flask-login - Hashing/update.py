import bcrypt
from flask_mysqldb import MySQL
from flask import Flask

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'holiday_house_rental_system'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)

with app.app_context():
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT user_id, password FROM secureusers")
    users = cursor.fetchall()

    for user in users:
        user_id = user[0]
        plain_password = user[4].encode('utf-8')

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password, salt)

      
        cursor.execute("UPDATE secureusers SET password = %s WHERE user_id = %s", (hashed_password, user_id))
        mysql.connection.commit()

cursor.close()

