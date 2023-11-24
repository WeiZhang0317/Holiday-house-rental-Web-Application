
DROP SCHEMA IF EXISTS houses_sys;
CREATE SCHEMA houses_sys;
USE houses_sys;


/* ----- Create the tables holiday_houses: ----- */

CREATE TABLE IF NOT EXISTS holiday_houses
(
  house_id INT PRIMARY KEY AUTO_INCREMENT,
  house_address VARCHAR(255) NOT NULL,
  number_of_bedrooms INT,
  number_of_bathrooms INT,
  maximum_occupancy INT,
  rental_per_night DECIMAL(10, 2),
  house_image VARCHAR(500)
);
ALTER TABLE holiday_houses AUTO_INCREMENT = 1001; 



/* ----- Insert data into the tables holiday_houses: ----- */
INSERT INTO holiday_houses (house_address, number_of_bedrooms, number_of_bathrooms, maximum_occupancy, rental_per_night,house_image) VALUES
('12 Queen St, Auckland', 3, 2, 5, 250.00, 'house1.jpg'),
('98 Lakefront Drive, Queenstown', 4, 3, 8, 500.00, 'house2.jpg'),
('23 Wellington Rd, Wellington', 2, 1, 4, 150.00, 'house3.jpg'),
('5 Church St, Christchurch', 3, 2, 6, 220.00, 'house4.jpg'),
('44 Tasman View Rd, Nelson', 5, 3, 10, 350.00, 'house5.jpg'),
('76 Marine Parade, Napier', 2, 2, 4, 180.00, 'house6.jpg'),
('32 High St, Dunedin', 3, 2, 5, 200.00, 'house7.jpg'),
('15 Sunny Bay Rd, Waiheke Island', 4, 2, 7, 450.00, 'house8.jpg'),
('90 Hilltop Ave, Taupo', 3, 1, 6, 175.00, 'house9.jpg'),
('55 Harbour View Rd, Coromandel', 4, 3, 9, 400.00, 'house10.jpg'),
('2 Forest Lane, Rotorua', 2, 2, 4, 190.00, 'house11.jpg'),
('77 Ocean View Rd, Tauranga', 3, 2, 5, 210.00, 'house12.jpg'),
('66 Mountain Rd, Wanaka', 4, 3, 8, 320.00, 'house13.jpg'),
('11 River Rd, Hamilton', 2, 1, 3, 130.00, 'house14.jpg'),
('30 Park Ave, Palmerston North', 3, 2, 6, 165.00, 'house15.jpg'),
('100 Coastal Hwy, Whangarei', 5, 4, 11, 500.00, 'house16.jpg'),
('88 Vineyard Rd, Blenheim', 3, 2, 5, 230.00, 'house17.jpg'),
('9 Cliff St, Kaikoura', 2, 1, 4, 145.00, 'house18.jpg'),
('40 Main St, New Plymouth', 4, 3, 7, 260.00, 'house19.jpg'),
('21 Beach Rd, Invercargill', 3, 2, 6, 190.00, 'house20.jpg');


/* ----- Create the tables USERS: ----- */
CREATE TABLE IF NOT EXISTS Users
(
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(100) NOT NULL,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  password VARCHAR(100) NOT NULL,
  phone_number VARCHAR(20),
  role_name VARCHAR(50) NOT NULL
);
ALTER TABLE users AUTO_INCREMENT = 101;  

/* ----- Insert data into the tables users: ----- */
/* ----- Insert customer data: ----- */
INSERT INTO users (username, name,  email, password, phone_number, role_name) VALUES 
('Alice123','Alice Smith', 'alice.smith@example.com', 'alicePass1', '0211000001', 'customer'),
('Bob123','Bob Johnson', 'bob.johnson@example.com',  'bobPass2', '0211000002', 'customer'),
('Carol123','Carol Williams', 'carol.williams@example.com', 'carolPass3', '0211000003', 'customer'),
('David123','David Brown', 'david.brown@example.com',  'davidPass4', '0211000004', 'customer'),
('Emma123','Emma Taylor', 'emma.taylor@example.com',  'emmaPass5', '0211000005', 'customer'),
('Frank22','Frank Wilson', 'frank.wilson@example.com', 'frankPass6', '0211000006', 'staff'),
('Grace11','Grace Miller', 'grace.miller@example.com', 'gracePass7', '0211000007', 'staff'),
('Henry33','Henry Davis', 'henry.davis@example.com', 'henryPass8', '0211000008', 'staff'),
('admin','Isabella Garcia', 'isabella.garcia@example.com', 'admin', '0211000009', 'staff-admin'),
('Isabella555','Isabella Garcia', 'isabella.garcia@example.com', 'isabellaPass9', '0211000009', 'staff-admin')
;

/* ----- Create the tables secureusers: ----- */
CREATE TABLE IF NOT EXISTS secureusers
(
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(100) NOT NULL,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100)  NOT NULL,
  password VARCHAR(255) NOT NULL,
  phone_number VARCHAR(20),
  role_name VARCHAR(50) NOT NULL
);
ALTER TABLE secureusers AUTO_INCREMENT = 101;  

/* ----- Insert data into the tables secureusers: ----- */
/* ----- Insert customer data: ----- */
INSERT INTO secureusers (username, name,  email, password, phone_number, role_name) VALUES 
('Alice123','Alice Smith', 'alice.smith@example.com', 'alicePass1', '0211000001', 'customer'),
('Bob123','Bob Johnson', 'bob.johnson@example.com',  'bobPass2', '0211000002', 'customer'),
('Carol123','Carol Williams', 'carol.williams@example.com', 'carolPass3', '0211000003', 'customer'),
('David123','David Brown', 'david.brown@example.com',  'davidPass4', '0211000004', 'customer'),
('Emma123','Emma Taylor', 'emma.taylor@example.com',  'emmaPass5', '0211000005', 'customer'),
('Frank22','Frank Wilson', 'frank.wilson@example.com', 'frankPass6', '0211000006', 'staff'),
('Grace11','Grace Miller', 'grace.miller@example.com', 'gracePass7', '0211000007', 'staff'),
('Henry33','Henry Davis', 'henry.davis@example.com', 'henryPass8', '0211000008', 'staff'),
('admin','Isabella Garcia', 'isabella.garcia@example.com', 'admin', '0211000009', 'staff-admin'),
('Isabella555','Isabella Garcia', 'isabella.garcia@example.com', 'isabellaPass9', '0211000009', 'staff-admin');

/* ----- Create the tables customers: ----- */
CREATE TABLE IF NOT EXISTS customer
(
  customer_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_number VARCHAR(50),
  address VARCHAR(1000),
  user_id INT,  
  FOREIGN KEY (user_id) REFERENCES secureusers(user_id)
);
ALTER TABLE customer AUTO_INCREMENT = 501;


/* ----- Insert data into the tables customer: ----- */
INSERT INTO customer (customer_number, address, user_id) VALUES 
('CN101','123 Maple Street, Auckland', 101),
('CN102', '456 Oak Avenue, Wellington', 102),
('CN103','789 Pine Road, Christchurch', 103),
('CN104','321 Birch Lane, Hamilton', 104),
('CN105','654 Cedar Path, Dunedin', 105);




/* ----- Create the tables Staffs: ----- */
CREATE TABLE IF NOT EXISTS Staff
(
  staff_id INT PRIMARY KEY AUTO_INCREMENT,
  staff_number VARCHAR(50),
  date_joined DATE NOT NULL,
  user_id INT,  
  FOREIGN KEY (user_id) REFERENCES secureusers(user_id)
);
ALTER TABLE Staff AUTO_INCREMENT = 201; 

INSERT INTO Staff (staff_number, date_joined, user_id) VALUES 
('STF106', '2023-01-10', 106),
('STF107', '2023-02-15', 107),
('STF108', '2023-03-20', 108),
('STF109', '2023-04-25', 109),
('STF110', '2023-01-25', 110);



















