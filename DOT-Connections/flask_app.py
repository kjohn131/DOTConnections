from flask import *
import sys
from os import environ
import re
import sqlite3 as sql
from flask import request
from flask import Flask
from bs4 import BeautifulSoup
import pandas as pd

debug=True

app = Flask(__name__, template_folder='templates')
app.secret_key = '0000'

@app.route('/')
def loginscreen():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        conn = sql.connect('C:\\sqlite\\DOTConnections.db')
        conn.row_factory = sql.Row
        cur = conn.cursor()
        sqlquery = "select exists(SELECT * FROM accounts WHERE username = ? AND password = ?)"
        args = (username,password)
        cur.execute(sqlquery, args)
        row = cur.fetchone()
        if row is None:
            msg = 'Incorrect username/password!'
        else:
            # Account doesnt exist or username/password incorrect
            session['loggedin'] = True
            return render_template('home.html')
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)
        # Check if account exists using MySQL
    cursor = sql.connect("C:\\sqlite\\DOTConnections.db")
    cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
    account = cursor.fetchone()
        # If account exists show error and validation checks
    if account:
        msg = 'Account already exists!'
    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        msg = 'Invalid email address!'
    elif not re.match(r'[A-Za-z0-9]+', username):
        msg = 'Username must contain only characters and numbers!'
    elif not username or not password or not email:
        msg = 'Please fill out the form!'
    else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
        cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
        mysql.connection.commit()
        msg = 'You have successfully registered!'

@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html')
    # User is not loggedin redirect to login page
    return render_template('layout.html')


@app.route('/searchdata', methods=['GET', 'POST'])
def searchdata():
    if request.method == 'POST':
        projectid = request.form['projectid']
        status = request.form['status']
        ConstructionCostEstimatefrom = request.form['fromname']
        ConstructionCostEstimateto = request.form['toname']
        district = request.form['district']
        county = request.form['county']
        con = sql.connect("C:\\sqlite\\DOTConnections.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        if projectid == '' and ConstructionCostEstimatefrom != '' and ConstructionCostEstimateto != '' and district != '' and county!= '':
            cur.execute('select * from DOT where ConstructionCostEstimate BETWEEN ? AND ? AND District = ? AND County = ?' , (ConstructionCostEstimatefrom, ConstructionCostEstimateto, district, county))
        elif projectid != '' and ConstructionCostEstimatefrom != '' and ConstructionCostEstimateto != '' and district == '' and county!= '':
            cur.execute('select * from DOT where ProjectID = ? AND ConstructionCostEstimate BETWEEN ? AND ? AND County = ?' , (projectid, ConstructionCostEstimatefrom, ConstructionCostEstimateto, county))
        elif projectid != '' and ConstructionCostEstimatefrom != '' and ConstructionCostEstimateto != '' and district != '' and county == '':
            cur.execute('select * from DOT where ProjectID = ? AND ConstructionCostEstimate BETWEEN ? AND ? AND District = ?' , (projectid, ConstructionCostEstimatefrom, ConstructionCostEstimateto, district))
        elif projectid != '' and ConstructionCostEstimatefrom == '' and ConstructionCostEstimateto == '' and district != '' and county != '':
            cur.execute('select * from DOT where ProjectID = ? AND District = ? AND County = ?' , (projectid, district ,county))
        elif projectid != '' and status == 'None' and ConstructionCostEstimatefrom == '' and ConstructionCostEstimateto == '' and district == '' and county == '':
            cur.execute('select * from DOT where ProjectID = ?' , (projectid,))
        elif projectid == '' and status != 'None' and ConstructionCostEstimatefrom == '' and ConstructionCostEstimateto == '' and district == '' and county == '':
            cur.execute('select * from DOT where Status = ?' , (status,))
        else:
            cur.execute('select * from DOT where ProjectID = ? AND ConstructionCostEstimate BETWEEN ? AND ? AND District = ? AND County = ?' , (projectid, ConstructionCostEstimatefrom, ConstructionCostEstimateto, district, county))
        results = cur.fetchall();
        con.close()
        return render_template('sqldatabase.html', results=results)
    return render_template('sqldatabase.html', results=[])


@app.route('/configure')
def configure():
    con = sql.connect("C:\\sqlite\\DOTConnections.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * from Config")
    results = cur.fetchall();
    print(results)
    con.close()
    return render_template('configure.html', results=results)


@app.route('/savedata', methods=['GET', 'POST'])
def savedata():
    con = sql.connect("C:\\sqlite\\DOTConnections.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    data = render_template('configure.html')
    df = pd.read_html(data)
    print(df)
    return render_template('configure.html')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))




if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)