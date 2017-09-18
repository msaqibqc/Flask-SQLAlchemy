"""
Flask Mysql Application:
File contains code related to the user by using the flask framework connected with mysql db.
It also includes functions to add, view, delete and authenticate the user presence in database.
Database connectivity is also handled in the same file.
"""

from flask import Flask, request, render_template, flash, session
from flaskext.mysql import MySQL


# Database connectivity

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'EmpData'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SECRET_KEY'] = "random string"
mysql.init_app(app)


@app.route("/")
def hello():
    """
    Renders the main page of application
    :return: web_page
    """
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('index.html')


@app.route("/index")
def index():
    """
    Renders the main page of application
    :return: web_page
    """
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('index.html')


@app.route("/logout")
def logout():
    """

    :return:
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
def new():
    """
    Method to add the new student in the DB.
    Fetches data from the form and then enters it in to DB  after connecting with DB.
    :return: message or index page
    """
    if not session.get('logged_in'):
        return render_template('login.html')
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
            cursor.execute("Insert into User values (" + str(id) + ",'" + username + "','" + password + "')")
            conn.commit()
            flash('User Added Successfully', 'error')
            return render_template('index.html')
    return "No User Added"


@app.route("/AllUsers")
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

    return render_template("all_users.html", data=data)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
    data = cursor.fetchone()
    if data is not None:
        flash('User logged in Successfully', 'error')
        session['logged_in'] = True
        return render_template('index.html')
    else:
        flash('Credentials are not correct!')
    return hello()


if __name__ == "__main__":
    app.run()