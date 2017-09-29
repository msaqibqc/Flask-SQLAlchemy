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

from flask_mysql_app.users_data.Users import Users
from flask_mysql_app.settings import mysql, app


mysql.init_app(app)
jwt = JWTManager(app)


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


@app.route("/index", methods=['POST', 'GET'])
@jwt_required
def index():
    """
    Welcomes the user on providing correct authorization token
    :return: web_page
    """
    data = get_jwt_identity()
    if not data['user']['session']:
        return jsonify({"Message": "Session expired"}), 400
    current_user = get_jwt_identity()
    return jsonify({'hello_from': current_user}), 200


@app.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    """
    Logout the user and expired the session and update the session in DB
    :return: response msg to user
    """
    data = get_jwt_identity()
    if not data['user']['session']:
        return jsonify({"Message": "Session expired"}), 400
    data = get_jwt_identity()
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
    return jsonify({"msg": "Successfully logged out"}), 200


@app.route("/remove", methods=['DELETE'])
@jwt_required
def remove():
    """
    Authenticates the username in the database and if username is available in db then
    deletes that user from database.
    :return: response message to user
    """
    data = get_jwt_identity()
    if not data['user']['session']:
        return jsonify({"Message": "Session expired"}), 400
    data = request.json
    user_id = data['id']
    username = user_id.strip()
    if username:
        conn = mysql.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE userId='" + user_id + "'")
        data = cursor.fetchone()
        if data is None:
            cursor.close()
            return jsonify({'message: ': "User is not available in database with this id"}), 400
        else:
            cursor.execute("DELETE FROM User WHERE userId = '" + user_id + "'")
            conn.commit()
            cursor.close()
            return jsonify({'message: ': "User removed successfully"}), 200
    return jsonify({'message: ': "Only spaces are entered"}), 400


@app.route('/new', methods=['GET', 'POST'])
@jwt_required
def new():
    """
    Method to add the new user in the DB.
    Fetches data from the form and then enters it in to DB  after connecting with DB.
    :return: response to user accordingly
    """
    data = get_jwt_identity()
    if not data['user']['session']:
        return jsonify({"Message": "Session expired"}), 400
    if request.method == 'POST':
        if not request.json['username'] or not request.json['password'] or not request.json['email']:
            return jsonify({'message: ': "Some fields are missing"}), 400
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
                                                                                         + "'", email="'" + email + "'")
                cursor.execute(query)
                conn.commit()
                cursor.close()
                return jsonify({'id': id}), 201
            else:
                cursor.close()
                return jsonify({'message: ': "Username or email already exist"}), 401
    return jsonify({'message: ': "No User Added"}), 401


@app.route("/AllUsers", methods=['GET'])
@jwt_required
def all_users():
    """
    Gets all the user from the database and then display them in response
    :return: response having all the user or invalid session message
    """
    data = get_jwt_identity()
    if not data['user']['session']:
        return jsonify({"Message": "Session expired"}), 400
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from User")
    data = cursor.fetchall()
    payload = []
    for result in data:
        content = {'id': result[0], 'username': result[1], 'password': result[2]}
        payload.append(content)
    cursor.close()
    return jsonify(payload), 200


@app.route('/login', methods=['POST'])
def login():
    """
    Gets the credentials from the user and authenticates that the user is available in the DB.
    And on availability of user in DB, logins the user.
    :return: token and login status
    """
    data = request.json
    username = data['username']
    password = data['password']

    cursor = mysql.connect().cursor()
    query = "SELECT * from User where Username={username} and Password={password}"
    query = query.format(username="'" + username + "'", password="'" + password + "'")
    cursor.execute(query=query)
    data = cursor.fetchone()
    if data is not None:
        expires = datetime.timedelta(days=365)
        user = Users(data[0], username, True, password)
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
            return jsonify({'access_token': access_token, 'status': 'User logged in'})
        else:
            id = response[0][0]
            access_token = create_access_token(identity={'user': user.get_data(), 'session_id': id,'device': device},
                                               expires_delta=expires)

            cursor.execute("UPDATE session SET is_active ='%d" % 1 + "', token='%s" % access_token +
                           "' WHERE userId = %d;" % user.id)
        conn.commit()
        cursor.close()
        return jsonify({'access_token': access_token, 'status': 'User logged in'})
    else:
        cursor.close()
        flash('Credentials are not correct!')
    return jsonify({'message': 'Credentials are not correct'}), 401


if __name__ == "__main__":
    app.run()
