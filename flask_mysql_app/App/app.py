"""
Flask authentication application:
File contains code related to the user by using the flask framework connected with mysql db.
It also includes functions to add, view, delete and authenticate the user presence in database.
Database connectivity is also handled in the same file.
Authenticates the user using the base of extended_jwt library
"""
from flask import Flask, request, flash, jsonify
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, \
    jwt_required ,get_raw_jwt, get_jti
from flaskext.mysql import MySQL
from flask_mysql_app.users_data.Users import Users
from flask_mysql_app.settings import mysql, app
import datetime


mysql.init_app(app)
jwt = JWTManager(app)


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    data = get_jwt_identity()
    data1 = get_raw_jwt()
    conn = mysql.get_db()
    cursor = conn.cursor()
    user_id = data['user']['id']
    session_id = data['session_id']
    cursor.execute("SELECT is_active FROM session WHERE userId='%d" % user_id + "' and sessionId='%d" % session_id + "'")
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
    if not data['session']:
        return jsonify({"Message": "Session expired"}), 400
    current_user = get_jwt_identity()
    return jsonify({'hello_from': current_user}), 200


@app.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    """
    Expires the token
    :return:
    """
    data = get_jwt_identity()
    if not data['session']:
        return jsonify({"Message": "Session expired"}), 400
    data = get_jwt_identity()
    get_jwt_identity()['session'] = False
    user_id = data['id']
    conn = mysql.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User WHERE userId='%d" % user_id + " '")
    data = cursor.fetchone()
    cursor.execute("UPDATE User SET user_session =%s" % 0 + " WHERE userId = %d;" % data[0])
    conn.commit()
    cursor.close()
    return jsonify({"msg": "Successfully logged out"}), 200


@app.route("/remove", methods=['DELETE'])
@jwt_required
def remove():
    """
    Authenticates the username in the database and if username is available in db then
    deletes that user from database.
    :return: web_page
    """
    data = get_jwt_identity()
    if not data['session']:
        return jsonify({"Message": "Session expired"}), 400
    data = request.json
    user_id = data['id']
    username = user_id.strip()
    if username:
        conn = mysql.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User where userId='" + user_id + "'")
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
    Method to add the new student in the DB.
    Fetches data from the form and then enters it in to DB  after connecting with DB.
    :return: message or index page
    """
    data = get_jwt_identity()
    if not data['session']:
        return jsonify({"Message": "Session expired"}), 400
    if request.method == 'POST':
        if not request.json['username'] or not request.json['password']:
            return jsonify({'message: ': "Some fields are missing"}), 200
        else:
            data = request.json
            username = data['username']
            password = data['password']
            conn = mysql.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * from User")
            data = cursor.fetchall()
            id = data[-1][0] + 1
            query = "INSERT INTO User VALUES ( {id}, {username}, {password}, {user_session}, {token} )"
            query = query.format(id=str(id), username="'" + username + "'", password="'" + password + "'",
                                 user_session=1, token='0')
            cursor.execute(query)
            conn.commit()
            cursor.close()
            return jsonify({'id': id}), 201
    return jsonify({'message: ': "No User Added"}), 401


@app.route("/AllUsers", methods=['GET'])
@jwt_required
def all_users():
    """
    Gets all the user from the database and then display them on web page.
    :return: web_page having all the users in the DB.
    """
    data = get_jwt_identity()
    if not data['user']['session']:
        return jsonify({"Message": "Session expired"}), 400
    data1 = get_raw_jwt()
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
    :return: web_page(Login or index page)
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

        # access_token = create_access_token(identity={'user': user.get_data(),'session_id': id}, expires_delta=expires)
        conn = mysql.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * from session")
        response = cursor.fetchall()
        id = response[-1][0] + 1
        access_token = create_access_token(identity={'user': user.get_data(), 'session_id': id}, expires_delta=expires)
        query = "INSERT INTO Session VALUES ( {id}, {userId}, {user_jti}, {token}, {is_active} )"
        query = query.format(id=str(id), userId="'" + str(user.id) + "'", user_jti="'" + "123" + "'",
                             token="'" + access_token + "'", is_active=1)
        cursor.execute(query)
        conn.commit()
        cursor.close()
        # data1 = get_raw_jwt()
        return jsonify({'access_token': access_token, 'status': 'User logged in'})
    else:
        cursor.close()
        flash('Credentials are not correct!')
    return jsonify({'message': 'Credentials are not correct'}), 401


if __name__ == "__main__":
    app.run()
