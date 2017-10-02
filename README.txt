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
 		email VARCHAR(25) NOT NULL,
		UNIQUE KEY(userName, email),
 		PRIMARY KEY(userId)
 		);
	- mysql> CREATE TABLE Session (
		sessionId INT NOT NULL AUTO_INCREMENT,
		userId INT NOT NULL,
		device VARCHAR(20) NOT NULL,
		token INT VARCHAR(400) NOT NULL,
		is_active INT NOT NULL,
		PRIMAR KEY(sessionId));

4. Selecting the database
	- Use EmpData;


5. Inserting row into the database
	- Insert into User values(1,’saqib’,’123’,’test1@gmail.com’);
	- Insert into Session values(1,’saqib’,’mobile’,’121212’,0);


6. Checking the data base table values
	- Select * from the User
	
	- This should show the tables with one row created.

	
Now rung the application, Run the file app.py
	- The server will start at http://127.0.0.1:5000


API Documentation

Login:

Hit: 	http://localhost:5000/login
	with credentials username and password as from data
	use username_or_password ‘saqib’ and password as ‘123’ and email ‘test1@gmail.com’
	as application/json form data
Response: Will return token and Login status

All Users:

Hit: 	http://localhost:5000/AllUsers
	with Authorization token in headers

Response: Will return all the users available in the datebase

Add New User:

Hit: 	http://localhost:5000/new
	with Authorization token in header
	with username and password and email values as application/json form data

Response: Will return the user id

Remove user:

Hit: 	http://localhost:5000/remove
	with Authorization token in header
	with id as application/json data

Response: Will return the status of user

Logout User:

Hit: 	http://localhost:5000/logout
	with Authorization token in header

Response: Logouts the User and expires the session


Change Password:

Hit: 	http://localhost:5000/change_password
	with Authorization token in header
	with old_password and new_passwors as application/json data

Response: Will return the status of password accordingly and removes all the sessions 	of that because of change of password.

Revoke Auth Token:

Hit: 	http://localhost:5000/revoke
	with Authorization token in header

Response: revokes the token and removes session and token from db.







