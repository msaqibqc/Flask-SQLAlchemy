"""
Settings file which contains all the data related to the data base connection and other settings
"""

from flaskext.mysql import MySQL

from flask import Flask

# Database connectivity

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'EmpData'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SECRET_KEY'] = "thisisverysecret123zabagal"