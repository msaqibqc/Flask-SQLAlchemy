"""
File contains all the tests covering the authentication process.
Tests includes the login , inserting users, getting user and token bases authentication.
"""

import pytest
import requests
import json
from random import randrange
from requests import codes
from faker import Faker


fake = Faker()


class TestingAuthentication():
    """
    Class tests all the end points for the user login endpoints which includes followings
    - Login user and setting session
    - Getting all the users
    - Adding new user
    - Deleting a new user based on user_id
    - Logging out user and expiring the session
    """
    def test_token_authentication(self):
        """
        Checking authentication with different scenarios.
        - Having auth token
        - Without auth token
        - With expired session
        - With valid token
        :return:
        """
        response = requests.get('http://localhost:5000/index')
        assert response.status_code == 401

        header = {'Content-Type': 'application/json', 'Authorization': ''}
        data = {"username_or_email": "test_user", "password": "test123"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(data), headers=header)
        assert response.status_code == 200

        data = response.json()
        assert data['access_token']
        header['Authorization'] = "Bearer " + data['access_token']

        response = requests.get('http://localhost:5000/index', headers=header)
        assert response.status_code == 200

        response = requests.delete('http://localhost:5000/logout', data=json.dumps(data), headers=header)
        assert response.status_code == 200

        response = requests.get('http://localhost:5000/index', headers=header)
        assert response.status_code == 400

    def test_user_login(self):
        """
        Checking login scenarios with valid credentials and invalid credentials  and then logging out user
        :return:
        """
        # login with wrong credentials
        headers = {'content-type': 'application/json', 'Authorization': ''}
        data = {"username_or_email": "username", "password": "password"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(data), headers=headers)
        assert response.status_code == 401
        assert "Credentials are not correct" in response.text

        # login with correct credentials

        data = {"username_or_email": "test_user", "password": "test123"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(data), headers=headers)
        assert response.status_code == 200
        resp = json.loads(response.text)
        headers['Authorization'] = "Bearer " + resp['access_token']
        assert resp['status'] == "User logged in"

        response = requests.delete('http://localhost:5000/logout', data=json.dumps(data), headers=headers)
        assert response.status_code == 200

        data = {"username_or_email": "test8@gmail.com", "password": "test123"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(data), headers=headers)
        assert response.status_code == 200
        resp = json.loads(response.text)
        headers['Authorization'] = "Bearer " + resp['access_token']
        assert resp['status'] == "User logged in"

        response = requests.delete('http://localhost:5000/logout', data=json.dumps(data), headers=headers)
        assert response.status_code == 200

    def test_adding_new_user_and_deleting(self):
        """
        Test includes scenario to add new user and then deletes that added user
        """
        headers = {'Content-Type': 'application/json', 'Authorization': ''}

        user_data = {"username_or_email": "test_user", "password": "test123"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(user_data), headers=headers)
        assert response.status_code == 200
        data = json.loads(response.text)
        headers['Authorization'] = 'Bearer %s' % data['access_token']

        # Getting fake information
        username = fake.name()
        password = fake.password()
        num = randrange(100000)
        email = str(num) + "@yahoo.com"

        data = {"username": username, "password": password , 'email': email}
        response = requests.post('http://localhost:5000/user', data=json.dumps(data), headers=headers)
        assert response.status_code == 201
        resp = json.loads(response.text)
        user_id = str(resp['id'])  # id of newly added user
        data = {'id': user_id}

        # deleting newly added user
        response = requests.delete('http://localhost:5000/user', data=json.dumps(data), headers=headers)
        assert response.status_code == 200

        # logging out the user
        response = requests.delete('http://localhost:5000/logout', data=json.dumps(user_data), headers=headers)
        assert response.status_code == 200

    def test_getting_all_the_users(self):
        """
        Test to get all the users with valid auth token and the checking the status code
        """

        headers = {'Content-Type': 'application/json'}
        data = {"username_or_email": "test_user", "password": "test123"}

        response = requests.post('http://localhost:5000/login', data=json.dumps(data), headers=headers)
        assert response.status_code == codes.OK
        data = response.json()
        assert data['access_token']
        token = {'Authorization': "Bearer " + data['access_token']}

        # Getting all the users
        response = requests.get('http://localhost:5000/user', headers=token)
        assert response.status_code == 200

        # logging out the user
        response = requests.delete('http://localhost:5000/logout',data=json.dumps(data), headers=token)
        assert response.status_code == 200

    def test_revoke_token(self):
        """
        Test to check that token revoked successfully and session expired.
        """
        headers = {'Content-Type': 'application/json', 'Authorization': ''}

        user_data = {"username_or_email": "test_user", "password": "test123"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(user_data), headers=headers)
        assert response.status_code == 200
        data = json.loads(response.text)
        headers['Authorization'] = 'Bearer %s' % data['access_token']

        response = requests.post('http://localhost:5000/token', data=json.dumps(data), headers=headers)
        data = json.loads(response.text)
        assert response.status_code == 200
        assert data['msg'] == "Token has been revoked"

        # revoking the token and testing the status code
        response = requests.post('http://localhost:5000/token', data=json.dumps(data), headers=headers)
        assert response.status_code == 400

    @pytest.mark.saqib
    def test_change_password(self):
        """
        Testing the password change functionality. And logging in with changed password.
        ALso again resetting the old password.
        """
        headers = {'Content-Type': 'application/json', 'Authorization': ''}

        user_data = {"username_or_email": "test_user", "password": "test123"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(user_data), headers=headers)
        assert response.status_code == 200
        data = json.loads(response.text)
        headers['Authorization'] = 'Bearer %s' % data['access_token']

        # Setting old and new password
        old_password = "test123"
        new_password = fake.password()
        data = {"old_password": old_password, "new_password": new_password}

        # Changing the password with given data
        response = requests.put('http://localhost:5000/user/update-password', data=json.dumps(data), headers=headers)
        data = json.loads(response.text)
        assert response.status_code == 200
        assert data['msg'] == "Password updated successfully"

        # checking the response on changing the password
        response = requests.put('http://localhost:5000/user/update-password', data=json.dumps(data), headers=headers)
        assert response.status_code == 400

        # logging in with new password and checking status
        user_data = {"username_or_email": "test_user", "password": new_password}
        response = requests.post('http://localhost:5000/login', data=json.dumps(user_data), headers=headers)
        assert response.status_code == 200
        data = json.loads(response.text)
        headers['Authorization'] = 'Bearer %s' % data['access_token']

        #  Check with wrong old password
        data = {"old_password": old_password, "new_password": new_password}
        response = requests.put('http://localhost:5000/user/update-password', data=json.dumps(data), headers=headers)
        data = json.loads(response.text)
        assert response.status_code == 400
        assert data['msg'] == "Old password is not correct"

        # setting data for resetting the password
        data = {"old_password": new_password, "new_password": old_password}

        # Resetting the old password
        response = requests.put('http://localhost:5000/user/update-password', data=json.dumps(data), headers=headers)
        data = json.loads(response.text)
        assert response.status_code == 200
        assert data['msg'] == "Password updated successfully"
