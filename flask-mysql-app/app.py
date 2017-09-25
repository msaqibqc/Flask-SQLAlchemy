"""
Flask Mysql Application:
File contains code related to the user by using the flask framework connected with mysql db.
It also includes functions to add, view, delete and authenticate the user presence in database.
Database connectivity is also handled in the same file.
Authenticates the user using the sessions provided by flask service
"""
from flask import Flask, request, render_template, flash, session, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager, \
    get_jwt_identity, jwt_required, get_raw_jwt
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


@app.route("/index", methods=['POST', 'GET'])
@jwt_required
def index():
    """
    Renders the main page of application
    :return: web_page
    """
    current_user = get_jwt_identity()
    return jsonify({'hello_from': current_user}), 200



@app.route('/expire', methods=['DELETE'])
@jwt_required
def expire():
    """
    Expires the token
    :return:
    """
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200


@app.route("/remove", methods=['GET', 'POST', 'DELETE'])
@jwt_required
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
            return jsonify({'message: ': "User is not available in database"}), 200
        else:
            cursor.execute("Delete from User Where userName = '" + username + "'")
            conn.commit()
            return jsonify({'message: ': "User removed successfully"}), 200
    return jsonify({'message: ': "Only spaces are entered"}), 200


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
            return jsonify({'message: ': "Some fields are missing"}), 200
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
            return jsonify({'id:': id})
    return jsonify({'message: ': "No User Added"}), 200


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
    data = cursor.fetchall()
    payload = []
    content = {}
    for result in data:
        content = {'id': result[0], 'username': result[1], 'password': result[2]}
        payload.append(content)
        content = {}
    return jsonify(payload)


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
    return jsonify({'message': 'Credentials are not correct'}), 200


if __name__ == "__main__":
    app.run()
