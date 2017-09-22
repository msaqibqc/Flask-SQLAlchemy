"""
Flask Mysql Application:
File contains code related to the user by using the flask framework connected with mysql db.
It also includes functions to add, view, delete and authenticate the user presence in database.
Database connectivity is also handled in the same file.
Authenticates the user using the sessions provided by flask service
"""
from flask import Flask, request, render_template, flash, session, abort, make_response, jsonify, url_for
from flask_httpauth import HTTPBasicAuth
import requests
from flask_jwt import JWT, current_identity
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager, \
    get_jwt_identity, jwt_required, get_raw_jwt
import json
from flaskext.mysql import MySQL

# Database connectivity
mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'EmpData'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SECRET_KEY'] = "random string"
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

blacklist = set()
mysql.init_app(app)
jwt = JWTManager(app)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


class User(object):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "User(id='%s')" % self.id

#
# def verify(username, password):
#     if not (username and password):
#         return False
#     # username = request.form['username']
#     # password = request.form['password']
#     cursor = mysql.connect().cursor()
#     cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
#     data = cursor.fetchone()
#     if data:
#         return User(id=data[0])

# jwt = JWT(app, verify, identity)

# @app.route("/protected")
# @jwt_required()
# def protected():
#     return '%s' % current_identity


@app.route("/")
def hello():
    """
    Renders the main page of application
    :return: web_page
    """
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('index.html')


@app.route("/index", methods=['POST', 'GET'])
@jwt_required
def index():
    """
    Renders the main page of application
    :return: web_page
    """
    # if not session.get('logged_in'):
    #     return render_template('login.html')
    current_user = get_jwt_identity()
    return jsonify({'hello_from': current_user}), 200
    # return render_template('index.html')


@app.route('/expire', methods=['DELETE'])
@jwt_required
def expire():
    """

    :return:
    """
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200


@app.route("/logout")
def logout():
    """
    Logout the user from website
    :return: web_page
    """
    session['logged_in'] = False
    return hello()


@app.route("/check_user")
def check_user():
    """
    Renders the page which takes the username and password of user and authenticates that
    username and password matches to the database. and responds accordingly.
    :return: web_page
    """
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('authenticate_user.html')


@app.route("/user_remove")
def user_remove():
    """
    Renders the page which takes username as input and if username is available in the database
    then deletes that user.
    :return: web_page
    """
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('remove.html')


@app.route("/Authenticate", methods=['GET', 'POST'])
def authenticate():
    """
    Authenticates the user and validates that the password and the username is valid
    as saved in the DB and shows the response accordingly.
    :return message
    """
    if not session.get('logged_in'):
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
    data = cursor.fetchone()
    if data is None:
        return "User is not available in the database"
    else:
        return "User is available in database"


@app.route("/remove", methods=['GET', 'POST'])
def remove():
    """
    Authenticates the username in the database and if username is available in db then
    deletes that user from database.
    :return: web_page
    """
    if not session.get('logged_in'):
        return render_template('login.html')
    username = request.form['username']
    username = username.strip()
    if username:
        conn = mysql.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * from User where userName='" + username + "'")
        data = cursor.fetchone()
        if data is None:
            return "User is not available in the database"
        else:
            cursor.execute("Delete from User Where userName = '" + username + "'")
            conn.commit()
            return "User removed successfully"
    return "Only spaces are entered"


@app.route('/saqib', methods=['GET'])
@jwt_required
def auth():
    return "Only spaces are entered"


@app.route('/new_user')
def add_user():
    """
    Renders the page which takes information from the user and adds new user to database.
    :return: web_page
    """
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('new.html')


@app.route('/new', methods=['GET', 'POST'])
@jwt_required
def new():
    """
    Method to add the new student in the DB.
    Fetches data from the form and then enters it in to DB  after connecting with DB.
    :return: message or index page
    """
    # if not session.get('logged_in'):
    #     return render_template('login.html')
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            return "Some fields are missing"
        else:
            username = request.form['username']
            password = request.form['password']
            conn = mysql.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * from User")
            data = cursor.fetchall()
            id = data[-1][0] + 1
            cursor.execute("Insert into User values (" + str(id) + ",'" + username + "','" + password + "','NULL')")
            conn.commit()
            # flash('User Added Successfully', 'error')
            return jsonify({'id:': id })
    return jsonify({'message: ':"No User Added" })


@app.route("/AllUsers")
@jwt_required
def all_users():
    """
    Gets all the user from the database and then display them on web page.
    :return: web_page having all the users in the DB.
    """
    if not session.get('logged_in'):
        return render_template('login.html')
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from User")
    # row_headers = [x[0] for x in cursor.description]
    data = cursor.fetchall()
    # json_data = []
    # for result in data:
    #     json_data.append(dict(zip(row_headers, result)))
    # return json.dumps(json_data)
    payload = []
    content = {}
    for result in data:
        content = {'id': result[0], 'username': result[1], 'password': result[2] }
        payload.append(content)
        content = {}
    return jsonify(payload)
    # data = json.dumps(data)
    # json.dumps([dict(ix) for ix in data])
    # data = dict(data)
    # return data


@app.route('/login', methods=['POST'])
def login():
    """
    Gets the credentials from the user and authenticates that the user is available in the DB.
    And on availability of user in DB, logins the user.
    :return: web_page(Login or index page)
    """
    username = request.form['username']
    password = request.form['password']
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
    data = cursor.fetchone()
    if data is not None:
        flash('User logged in Successfully', 'error')
        session['logged_in'] = True
        access_token = create_access_token(identity=username)
        conn = mysql.get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE User SET token = '" + str(access_token) + "' WHERE userId = " + str(data[0]) + ";")
        conn.commit()
        return jsonify({'access_token': access_token, 'login': 'successful'}), 201
    else:
        flash('Credentials are not correct!')
    return jsonify({'message':'Credentials are not correct'}), 200


if __name__ == "__main__":
    app.run()

