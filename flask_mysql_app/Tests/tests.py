"""
File contains all the tests covering the authentication process.
Tests includes the login , inserting users, getting user and token bases authentication.
"""

import pytest
import requests
from requests import codes

from flask_mysql_app.App import app
import json


class TestingAuthentication:
    def test_token_authentication(self):
        """
        Checking authentication without token
        :return:
        """
        response = requests.get('http://localhost:5000/index')
        assert response.status_code == 401


        # assert (response.json(), {'hello': 'world'})
        # assert 'Hello, World!' in response
        #
        # assert 1, 1

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

        data = {"username": "saqib", "password": "123"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(data), headers=headers)
        assert response.status_code == 200
        data = json.loads(response.text)
        headers = 'Authorization: Bearer %s' % data['access_token']
        assert data['login'] == "successful"

    def test_adding_new_user(self):
        """

        :return:
        """
        headers = {'Content-Type': 'application/json', 'Authorization': ''}

        data = {"username": "saqib", "password": "123"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(data), headers=headers)
        assert response.status_code == 200
        data = json.loads(response.text)
        headers['Authorization'] = 'Bearer %s' % data['access_token']

        data = {"username": "javed", "password": "java"}
        response = requests.post('http://localhost:5000/new', data=json.dumps(data), headers=headers)
        assert response.status_code == 201
        # data = json.loads(response.text)

    @pytest.mark.saqib
    def test_getting_all_the_users(self):
        """

        :return:
        """

        headers = {'Content-Type': 'application/json'}
        data = {"username": "aslam", "password": "123"}
        response = requests.post('http://localhost:5000/login', data=json.dumps(data), headers=headers)
        assert response.status_code == codes.OK
        data = response.json()
        assert data['access_token']
        token = {'Authorization': "Bearer " + data['access_token']}
        response = requests.get('http://localhost:5000/AllUsers', headers=token)
        assert response.status_code == 200





