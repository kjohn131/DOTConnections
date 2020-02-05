from flask import *
import sys
from os import environ
import re
import sqlite3 as sql
from flask import request
from flask import Flask
from bs4 import BeautifulSoup
import pandas as pd
from flask import jsonify
import json
from pandas.io.json import json_normalize
import numpy as np
from numpy import array
import itertools

debug=True

app = Flask(__name__, template_folder='templates')
app.secret_key = '0000'

@app.route('/')
def loginscreen():
    return render_template('index.html')

@app.route('/login.html', methods=['GET', 'POST'])
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
        conn = sql.connect("C:\\sqlite\\DOTConnections.db")
        rows=conn.execute('SELECT username FROM accounts where username IN (username)')
        rows=list(rows)
        if len(rows) !=0:
            for row in rows[0]:
                if row==username:
                    msg = 'Account already exists!'
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        
        #msg = 'yha aayaa'
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
        else:
            conn.execute('INSERT INTO accounts VALUES (?, ?, ?)', (username, password, email))
            conn.commit()

        msg = 'You have successfully registered!'

    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)


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
    con.close()
    return render_template('configure.html', results=results)


@app.route('/savedata', methods=['GET', 'POST'])
def savedata():
    con = sql.connect("C:\\sqlite\\DOTConnections.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    df = pd.DataFrame(data)
    print(df)

@app.route('/SaveFile', methods=['POST', 'GET'])
def SaveFile():
    send_back = {"status": "failed"}
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(data)
            data = array(data)
            data = np.split(data, 21)
            print(data)
            data = pd.DataFrame(np.vstack(data))
            data = data.replace('<input type="text" value="', '', regex=True)
            data = data.replace('" style="text-align: center;">','',regex=True)
            print(data)
            con = sqlite3.connect("C:\\sqlite\\DOTConnections.db")
            data.to_sql('Config', con, if_exists='replace', index=False)
            con.close()
            send_back["status"] = "success"
        except Error as err:
            send_back["status"] = str(err)
    return jsonify(send_back)


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