# Flask-SQLAlchemy

API Documentation

Login:

Hit: 	localhost:5000/login
	with credentials username and password as from data

Response: Will return token and Login status

All Users:

Hit: 	localhost:5000/AllUsers
	with Authorization token in headers

Response: Will return all the users available in the datebase

Add New User:

Hit: 	localhost:5000/new
	with Authorization token in header
	with username and password values as from data

Response: Will return the user id

Remove user:

Hit: 	localhost:5000/remove
	with Authorization token in header
	with username as from data

Response: Will return the status of user

Expire token:

Hit: 	localhost:5000/expire
	with Authorization token in header

Response: Logouts the User







