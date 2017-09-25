# Flask-Authentication API 


To start the project:

Clone the Project:

1. cd Flask-SQLAlchemy/

2. Open terminal

Type following commands:
	mysql -uroot 

3. Run the following MySql commands

	- mysql> CREATE DATABASE EmpData;

	- mysql> CREATE TABLE User(
 		userId INT NOT NULL AUTO_INCREMENT,
 		userName VARCHAR(100) NOT NULL,
 		password VARCHAR(40) NOT NULL,
		token VARCHAR(300) NOT NULL,
 		PRIMARY KEY(userId)
 		);

4. Selecting the database
	- Use EmpData;


5. Inserting row into the database
	- Insert into User values(1,’saqib’,’123’,’121212’);


6. Checking the data base table values
	- Select * from the User
	
	- This should show the tables with one row created.

	
Now rung the application, Run the file app.py
	- The server will start at http://127.0.0.1:5000


API Documentation

Login:

Hit: 	http://localhost:5000/login
	with credentials username and password as from data
	use username ‘saqib’ and password as ‘123’

Response: Will return token and Login status

All Users:

Hit: 	http://localhost:5000/AllUsers
	with Authorization token in headers

Response: Will return all the users available in the datebase

Add New User:

Hit: 	http://localhost:5000/new
	with Authorization token in header
	with username and password values as from data

Response: Will return the user id

Remove user:

Hit: 	http://localhost:5000/remove
	with Authorization token in header
	with username as from data

Response: Will return the status of user

Expire token:

Hit: 	http://localhost:5000/expire
	with Authorization token in header

Response: Logouts the User







