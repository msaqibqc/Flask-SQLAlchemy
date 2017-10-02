"""
Flask authentication application:
File contains code related to the user by using the flask framework connected with mysql db.
It also includes functions to add, view, delete and authenticate the user presence in database.
Database connectivity is also handled in the same file.
Authenticates the user using the base of extended_jwt library
"""

import datetime

from flask import request, flash, jsonify
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, \
    jwt_required

from flask_restful import Api, Resource
from flask_mysql_app.users_data.Users import Users
from flask_mysql_app.settings import mysql, app

mysql.init_app(app)
jwt = JWTManager(app)
api = Api(app)


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    """
    Function callback when jwt_required is called
    :param identity: user_identity
    :return: identity of user
    """
    data = get_jwt_identity()
    conn = mysql.get_db()
    cursor = conn.cursor()
    user_id = data['user']['id']
    session_id = data['session_id']
    cursor.execute("SELECT is_active FROM session WHERE userId='%d" % user_id +
                   "' AND sessionId='%d" % session_id + "'")
    data = cursor.fetchone()
    if data[0] == 0:
        cursor.close()
        get_jwt_identity()['user']['session'] = False

    return get_jwt_identity()


class IndexOfUser(Resource):
    def send_response(self, data, status_code):
        return data, status_code

    @jwt_required
    def get(self):
        data = get_jwt_identity()
        if not data['user']['session']:
            data = {"Message": "Session expired"}
            return self.send_response(data, 400)
        current_user = get_jwt_identity()
        data = {'hello_from': current_user}
        return self.send_response(data, 200)


class UserLogout(Resource):
    def send_response(self, data, status_code):
        return data, status_code

    @jwt_required
    def delete(self):
        """
        Logout the user and expired the session and update the session in DB
        :return: response msg to user
        """
        data = get_jwt_identity()
        if not data['user']['session']:
            data = {"Message": "Session expired"}
            return self.send_response(data, 400)

        get_jwt_identity()['user']['session'] = False
        user_id = data['user']['id']
        session_id = data['session_id']
        device = data['device']
        conn = mysql.get_db()
        cursor = conn.cursor()

        cursor.execute("UPDATE session SET is_active=%s" % 0 + " WHERE userId = '%d" % user_id +
                       "' AND sessionId='%d" % session_id + "' AND device='%s" % device + "'")
        conn.commit()
        cursor.close()
        data = {"msg": "Successfully logged out"}
        return self.send_response(data, 200)


class Token(Resource):
    def send_response(self, data, status_code):
        return data, status_code

    @jwt_required
    def post(self):
        """
        Revokes the token of logged_in user
        """
        data = get_jwt_identity()
        if not data['user']['session']:
            data = {"Message": "Session expired"}
            return self.send_response(data, 400)

        data = get_jwt_identity()
        get_jwt_identity()['user']['session'] = False
        user_id = data['user']['id']
        session_id = data['session_id']
        device = data['device']
        conn = mysql.get_db()
        cursor = conn.cursor()

        cursor.execute("UPDATE session SET is_active=%s" % 0 + ", token='%s" % 0 + "' WHERE userId = '%d" % user_id +
                       "' AND sessionId='%d" % session_id + "' AND device='%s" % device + "'")
        conn.commit()
        cursor.close()
        data = {"msg": "Token has been revoked"}

        return self.send_response(data, 200)

    @jwt_required
    def delete(self):
        """
        Endpoint which expires all the tokens of all logged in users
        :return:
        """
        data = get_jwt_identity()
        if not data['user']['session']:
            data = {"Message": "Session expired"}
            return self.send_response(data, 400)

        conn = mysql.get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE session SET is_active ='%d" % 0 + "', token='%s" % 0 + "'")
        conn.commit()
        cursor.close()
        data = {'msg': 'All tokens expired'}
        return self.send_response(data, 400)


class User(Resource):
    def send_response(self, data, status_code):
        return data, status_code

    @jwt_required
    def delete(self):
        """
        Authenticates the username in the database and if username is available in db then
        deletes that user from database.
        :return: response message to user
        """
        data = get_jwt_identity()
        if not data['user']['session']:
            data = {"Message": "Session expired"}
            return self.send_response(data, 400)

        data = request.json
        user_id = data['id']
        user_id = user_id.strip()
        if user_id:
            conn = mysql.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE userId='" + user_id + "'")
            data = cursor.fetchone()
            if data is None:
                cursor.close()
                data = {'message: ': "User is not available in database with this id"}
                return self.send_response(data, 400)
            else:
                cursor.execute("DELETE FROM User WHERE userId = '" + user_id + "'")
                conn.commit()
                cursor.close()
                data = {'message: ': "User removed successfully"}
                return self.send_response(data, 200)

        data = {'message: ': "Only spaces are entered"}
        return self.send_response(data, 400)

    @jwt_required
    def post(self):
        """
        Method to add the new user in the DB.
        Fetches data from the form and then enters it in to DB  after connecting with DB.
        :return: response to user accordingly
        """
        data = get_jwt_identity()
        if not data['user']['session']:
            data = {"Message": "Session expired"}
            return self.send_response(data, 400)

        if not request.json['username'] or not request.json['password'] or not request.json['email']:
            data = {'message: ': "Some fields are missing"}
            return self.send_response(data, 400)
        else:
            data = request.json
            username = data['username']
            password = data['password']
            email = data['email']

            conn = mysql.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * from User WHERE username='%s" % username + "' OR email='%s" % email + "'")
            data = cursor.fetchall()

            if not data:
                cursor.execute("SELECT * from User")
                data = cursor.fetchall()
                id = data[-1][0] + 1
                query = "INSERT INTO User VALUES ( {id}, {username}, {password}, {email} )"
                query = query.format(id=str(id), username="'" + username + "'", password="'" + password
                                                                                         + "'",
                                     email="'" + email + "'")
                cursor.execute(query)
                conn.commit()
                cursor.close()
                data = {'id': id}
                return self.send_response(data, 201)
            else:
                cursor.close()
                data = {'message: ': "Username or email already exist"}
                return self.send_response(data, 401)

    @jwt_required
    def get(self):
        """
        Gets all the user from the database and then display them in response
        :return: response having all the user or invalid session message
        """
        data = get_jwt_identity()
        if not data['user']['session']:
            data = {"Message": "Session expired"}
            return self.send_response(data, 400)

        cursor = mysql.connect().cursor()
        cursor.execute("SELECT * from User")
        data = cursor.fetchall()
        payload = []
        for result in data:
            content = {'id': result[0], 'username': result[1], 'password': result[2]}
            payload.append(content)
        cursor.close()
        data = (payload)
        return self.send_response(data, 200)

    @jwt_required
    def put(self):
        """
        Changes the password of the user and responds accordingly
        :return: response msg to user
        """
        user_data = get_jwt_identity()
        if not user_data['user']['session']:
            data = {"Message": "Session expired"}
            return self.send_response(data, 400)

        data = request.json
        old_password = data['old_password']
        new_password = data['new_password']
        user_id = user_data['user']['id']
        old_password = old_password.strip()
        new_password = new_password.strip()
        if old_password and new_password:
            conn = mysql.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE userId='%d" % user_id + "' and password='%s" % old_password + "'")
            data = cursor.fetchone()
            if data is None:
                cursor.close()
                data = {'message: ': "Old password is not correct"}
                return self.send_response(data, 400)
            else:
                cursor.execute("UPDATE User SET password='%s" % new_password + "' WHERE userId ='%d" % user_id + "'")
                conn.commit()
                cursor.execute(
                    "UPDATE session SET is_active=%s" % 0 + ", token='%s" % 0 + "' WHERE userId ='%d" % user_id + "'")
                conn.commit()
                cursor.close()
                data = {'msg': "Password updated successfully"}
                return self.send_response(data, 200)
        data = {'message: ': "Only spaces are entered"}
        return self.send_response(data, 400)


class UserLogin(Resource):
    def send_response(self, data, status_code):
        return data, status_code

    def post(self):
        """
        Gets the credentials from the user and authenticates that the user is available in the DB.
        And on availability of user in DB, logins the user.
        :return: token and login status
        """
        data = request.json
        username_or_email = data['username_or_email']
        password = data['password']

        cursor = mysql.connect().cursor()
        query = "SELECT * from User WHERE  (email={username_or_email} " \
                "OR Username={username_or_email}) AND Password={password} "
        query = query.format(username_or_email="'" + username_or_email + "'", password="'" + password + "'")
        cursor.execute(query=query)
        data = cursor.fetchone()
        if data is not None:
            expires = datetime.timedelta(days=365)
            user = Users(data[0], username_or_email + "'", True, password)
            conn = mysql.get_db()
            cursor = conn.cursor()
            device = "mobile"
            cursor.execute("SELECT * from session where userId='%d" % user.id + "' and device ='%s" % device + "'")
            response = cursor.fetchall()
            if not response:
                cursor.execute("SELECT * from session")
                response = cursor.fetchall()
                id = response[-1][0] + 1
                access_token = create_access_token(identity={'user': user.get_data(),
                                                             'session_id': id, 'device': device}, expires_delta=expires)
                query = "INSERT INTO Session VALUES ( {id}, {userId}, {device}, {token}, {is_active} )"
                query = query.format(id=str(id), userId="'" + str(user.id) + "'", device="'" + "mobile" + "'",
                                     token="'" + access_token + "'", is_active=1)
                cursor.execute(query)
                conn.commit()
                cursor.close()
                data = {'access_token': access_token, 'status': 'User logged in'}
                return self.send_response(data, 200)
            else:
                id = response[0][0]
                access_token = create_access_token(
                    identity={'user': user.get_data(), 'session_id': id, 'device': device},
                    expires_delta=expires)

                cursor.execute("UPDATE session SET is_active ='%d" % 1 + "', token='%s" % access_token +
                               "' WHERE userId = %d;" % user.id)
            conn.commit()
            cursor.close()
            data = {'access_token': access_token, 'status': 'User logged in'}
            return self.send_response(data, 200)
        else:
            cursor.close()

            data = {'message': 'Credentials are not correct'}
            return self.send_response(data, 401)


api.add_resource(IndexOfUser, '/index')
api.add_resource(Token, '/token', '/token/expire-all-tokens')
api.add_resource(User, '/user', '/user/update-password')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')

if __name__ == "__main__":
    app.run()
