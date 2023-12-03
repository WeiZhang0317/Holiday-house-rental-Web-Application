
# Holiday house rental Web Application



## Login details

#### Customer Login
* USER NAME: Alice123
* PASSWORD: alicePass1

  #### Staff Login
* USER NAME: Frank22
* PASSWORD: frankPass6

  #### Admin Login
* USER NAME: admin
* PASSWORD: admin

  #### Note
  * If the admin created a staff, the default password is 56789, the password will be edited by users themselves
  * If the admin created a customer, the default password is 123456, the password will be edited by user themselves

## Features
1. User authentication (login, logout, registration)
2. Password encryption using bcrypt
3. Role-based access control (customer, staff, staff-admin)
4. CRUD operations for holiday house listings
5. Profile management for users

## Installation

1. Python latest version
2. Flask
3. MySQL
4. bcrypt


## Setup
Install required Python packages:

* Copy code: 
pip install flask mysql-connector-python bcrypt

## Configuration
Set up the MySQL database and update the connect.py file with your database credentials.

# Database design
*mysql database house_sys is used
![alt text](https://github.com/WeiZhang0317/639-assignment1/blob/main/holiday%20house%20rental%20sys/static/readme1.jpg)

# The relation between endpoint and html template, also its functions
## Part1  
![alt text](https://github.com/WeiZhang0317/639-assignment1/blob/main/holiday%20house%20rental%20sys/static/readme2.jpg)

## Part2  
![alt text](https://github.com/WeiZhang0317/639-assignment1/blob/main/holiday%20house%20rental%20sys/static/readme3.jpg)
