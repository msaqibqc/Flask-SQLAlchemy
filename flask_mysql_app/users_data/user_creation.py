"""
File to create a new user
"""

from flask_mysql_app.users_data.Users import Users
import json , requests


class CreateUser:
    """

    """
    def create_user(self):
        headers = {'Content-Type': 'application/json'}
        username = "test_user"
        password = "test123"
        data = {"username": username, "password": password}
        response = requests.post('http://localhost:5000/new', data=json.dumps(data), headers=headers)
        response = json.dumps(response)
        user = Users(id=response['id'], username=username, session=True, password=password)
        return user

