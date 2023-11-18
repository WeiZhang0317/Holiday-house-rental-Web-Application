
DROP SCHEMA IF EXISTS holiday_house_rental_system;
CREATE SCHEMA holiday_house_rental_system;
USE holiday_house_rental_system;


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


/* ----- Create the tables ROLES: ----- */

CREATE TABLE IF NOT EXISTS Roles
(
  role_id VARCHAR(1) PRIMARY KEY NOT NULL,
  role_name VARCHAR(50) NOT NULL
);


/* ----- Create the tables USERS: ----- */
CREATE TABLE IF NOT EXISTS Users
(
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  password VARCHAR(100) NOT NULL,
  phone_number VARCHAR(20),
  role_id VARCHAR(1) NOT NULL,
  FOREIGN KEY (role_id) REFERENCES Roles(role_id)
);

ALTER TABLE Users AUTO_INCREMENT = 101;


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

/* ----- Insert data into the tables roles: ----- */

INSERT INTO Roles (role_id, role_name) VALUES 
('A', 'customer'), 
('B', 'staff'), 
('C', 'admin');

/* ----- Insert data into the tables users: ----- */
/* ----- Insert customer data: ----- */
INSERT INTO Users (name, email, password, phone_number, role_id) VALUES 
('Alice Smith', 'alice.smith@example.com', 'alicePass1', '0211000001', 'A'),
('Bob Johnson', 'bob.johnson@example.com', 'bobPass2', '0211000002', 'A'),
('Carol Williams', 'carol.williams@example.com', 'carolPass3', '0211000003', 'A'),
('David Brown', 'david.brown@example.com', 'davidPass4', '0211000004', 'A'),
('Emma Taylor', 'emma.taylor@example.com', 'emmaPass5', '0211000005', 'A');

/* ----- Insert staff data: ----- */
INSERT INTO Users (name, email, password, phone_number, role_id) VALUES 
('Frank Wilson', 'frank.wilson@example.com', 'frankPass6', '0211000006', 'B'),
('Grace Miller', 'grace.miller@example.com', 'gracePass7', '0211000007', 'B'),
('Henry Davis', 'henry.davis@example.com', 'henryPass8', '0211000008', 'B');

/* ----- Insert admin data: ----- */
INSERT INTO Users (name, email, password, phone_number, role_id) VALUES 
('Isabella Garcia', 'isabella.garcia@example.com', 'isabellaPass9', '0211000009', 'C');
