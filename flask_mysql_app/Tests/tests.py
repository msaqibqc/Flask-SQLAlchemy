"""
File contains all the tests covering the authentication process.
Tests includes the login , inserting users, getting user and token bases authentication.
"""

import pytest
import requests
from requests import codes

from flask_mysql_app.App import app
from flask_mysql_app.users_data.user_creation import CreateUser
import json

url = ""
class TestingAuthentication():

    def test_token_authentication(self):
        """
        Checking authentication without token
        :return:
        """
        response = requests.get('http://localhost:5000/index')
        assert response.status_code == 401

        header = {'Content-Type': 'application/json', 'Authorization': ''}
        data = {"username": "test_user", "password": "test123"}
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
        Checking login scenarios
        :return:
        """
        # login with wrong credentials
        headers = {'content-type': 'application/json', 'Authorization': ''}
        data = {"username": "23", "password": "213"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(data), headers=headers)
        assert response.status_code == 401
        assert "Credentials are not correct" in response.text

        # login with correct credentials

        data = {"username": "test_user", "password": "test123"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(data), headers=headers)
        assert response.status_code == 200
        resp = json.loads(response.text)
        headers['Authorization'] = "Bearer " + resp['access_token']
        assert resp['status'] == "User logged in"

        response = requests.delete('http://localhost:5000/logout', data=json.dumps(data), headers=headers)
        assert response.status_code == 200

    @pytest.mark.saqib
    def test_adding_new_user(self):
        """

        :return:
        """
        headers = {'Content-Type': 'application/json', 'Authorization': ''}

        user_data = {"username": "test_user", "password": "test123"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(user_data), headers=headers)
        assert response.status_code == 200
        data = json.loads(response.text)
        headers['Authorization'] = 'Bearer %s' % data['access_token']

        data = {"username": "Test_khochi", "password": "khocha123"}
        response = requests.post('http://localhost:5000/new', data=json.dumps(data), headers=headers)
        assert response.status_code == 201
        resp = json.loads(response.text)
        user_id = str(resp['id'])
        data = {'id': user_id}
        response = requests.delete('http://localhost:5000/remove', data=json.dumps(data), headers=headers)
        assert response.status_code == 200

        response = requests.delete('http://localhost:5000/logout', data=json.dumps(user_data), headers=headers)
        assert response.status_code == 200

    def test_getting_all_the_users(self):
        """

        :return:
        """

        headers = {'Content-Type': 'application/json'}
        data = {"username": "test_user", "password": "test123"}

        response = requests.post('http://localhost:5000/login', data=json.dumps(data), headers=headers)
        assert response.status_code == codes.OK
        data = response.json()
        assert data['access_token']
        token = {'Authorization': "Bearer " + data['access_token']}
        response = requests.get('http://localhost:5000/AllUsers', headers=token)
        assert response.status_code == 200

        response = requests.delete('http://localhost:5000/logout',data=json.dumps(data), headers=token)
        assert response.status_code == 200






