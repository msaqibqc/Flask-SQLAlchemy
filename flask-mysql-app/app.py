from flask import Flask, request, render_template, flash
from flaskext.mysql import MySQL


mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'EmpData'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route("/")
def hello():
    """
    Just shows message on the web page
    :return:
    """
    return render_template('index.html')


@app.route("/check_user")
def check_user():
    """
    Just shows message on the web page
    :return:
    """
    return render_template('authenticate_user.html')


@app.route("/Authenticate", methods=['GET', 'POST'])
def authenticate():
    """
    Authenticates the user and validates that the password and the user name is valid
    as saved in the DB and shows the response accordingly.
    :return:
    """
    username = request.form['username']
    password = request.form['password']
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
    data = cursor.fetchone()
    if data is None:
        return "Username or Password is wrong"
    else:
        return "Logged in successfully"


@app.route('/new_user')
def add_user():
    """

    :return:
    """
    return render_template('new.html')


@app.route('/new', methods=['GET', 'POST'])
def new():
    """
    Method to add the new student in the DB.
    :return: page with newly added student
    """
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash('Please enter all the fields', 'error')
        else:
            username = request.form['username']
            password = request.form['password']
            cursor = mysql.connect().cursor()
            cursor.execute("SELECT * from User")
            data = cursor.fetchall()
            id = data[-1][0] + 1
            cursor.execute("Insert into User values (" + str(id) + ",'" + username + "','" + password + "')")
            cursor.commit()
            return render_template('index.html')
    return "No User Added"


@app.route("/AllUsers")
def all_users():
    """
    Authenticates the user and validates that the password and the user name is valid
    as saved in the DB and shows the response accordingly.
    :return:
    """
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from User")
    data = cursor.fetchall()

    return render_template("all_users.html", data=data)


if __name__ == "__main__":
    app.run()