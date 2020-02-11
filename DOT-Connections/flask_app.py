from flask import *
import sys
from os import environ
import re
import sqlite3 as sql
from flask import request
from flask import Flask, flash
from bs4 import BeautifulSoup
import pandas as pd
from flask import jsonify
import json
from pandas.io.json import json_normalize
import numpy as np
from numpy import array
import itertools
import re

debug=True

app = Flask(__name__, template_folder='templates')
app.secret_key = '0000'

@app.route('/')
def loginscreen():
    return render_template('index.html')

@app.route('/comingsoon')
def comingsoon():
    return render_template('comingsoon.html')

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
        conn = sql.connect("C:\\sqlite\\DOTConnections.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        sqlquery = "SELECT * FROM accounts WHERE username = ? AND password = ?"
        args = (username,password)
        cur.execute(sqlquery, args)
        row = cur.fetchone()
        if row is None:
            flash('Incorrect username/password!')
        else:
            # Account doesnt exist or username/password incorrect
            session['loggedin'] = True
            session['username'] = row['username']
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
        return render_template('home.html', username = session['username'])
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
        if projectid == '' and status !='' and ConstructionCostEstimatefrom != '' and ConstructionCostEstimateto != '' and district != '' and county!= '':
            cur.execute('select * from DOT where Status = ? AND ConstructionCostEstimate BETWEEN ? AND ? AND District = ? AND County = ?' , (status, ConstructionCostEstimatefrom, ConstructionCostEstimateto, district, county))
        
        elif projectid == '' and status !='' and ConstructionCostEstimatefrom == '' and ConstructionCostEstimateto == '' and district != '' and county == '':
            cur.execute('select * from DOT where Status = ? AND District = ?' , (status, district))

        elif projectid == '' and status !='' and ConstructionCostEstimatefrom == '' and ConstructionCostEstimateto == '' and district == '' and county != '':
            cur.execute('select * from DOT where Status = ? AND County = ?' , (status, county))

        elif projectid == '' and status !='' and ConstructionCostEstimatefrom == '' and ConstructionCostEstimateto == '' and district != '' and county != '':
            cur.execute('select * from DOT where Status = ? AND District = ? AND County = ?' , (status, district, county))

        elif projectid != '' and status !='' and ConstructionCostEstimatefrom == '' and ConstructionCostEstimateto == '' and district != '' and county != '':
            cur.execute('select * from DOT where ProjectID = ? AND Status = ? AND District = ? AND County = ?' , (projectid, status, district, county))

        elif projectid == '' and status !='' and ConstructionCostEstimatefrom != '' and ConstructionCostEstimateto != '' and district == '' and county == '':
            cur.execute('select * from DOT where Status = ? ConstructionCostEstimate BETWEEN ? AND ?' , (status, ConstructionCostEstimatefrom, ConstructionCostEstimateto))

        elif projectid != '' and status !='' and ConstructionCostEstimatefrom != '' and ConstructionCostEstimateto != '' and district == '' and county!= '':
                    cur.execute('select * from DOT where ProjectID = ? AND Status = ? AND ConstructionCostEstimate BETWEEN ? AND ? AND County = ?' , (projectid, status, ConstructionCostEstimatefrom, ConstructionCostEstimateto, county))
        
        elif projectid != '' and status !='' and ConstructionCostEstimatefrom != '' and ConstructionCostEstimateto != '' and district != '' and county == '':
            cur.execute('select * from DOT where ProjectID = ? Status = ? AND ConstructionCostEstimate BETWEEN ? AND ? AND District = ?' , (projectid, status, ConstructionCostEstimatefrom, ConstructionCostEstimateto, district))
        
        elif projectid != '' and status !='' and ConstructionCostEstimatefrom == '' and ConstructionCostEstimateto == '' and district != '' and county != '':
            cur.execute('select * from DOT where Status = ? AND ProjectID = ? AND District = ? AND County = ?' , (projectid,status ,district ,county))
        
        elif projectid != '' and status != '' and ConstructionCostEstimatefrom == '' and ConstructionCostEstimateto == '' and district == '' and county == '':
            cur.execute('select * from DOT where Status = ? AND ProjectID = ?' , (status, projectid ))
        
        elif projectid == '' and status != '' and ConstructionCostEstimatefrom == '' and ConstructionCostEstimateto == '' and district == '' and county == '':
            cur.execute('select * from DOT where Status = ?' , (status,))
        else:
            cur.execute('select * from DOT where Status = ? AND ProjectID = ? AND ConstructionCostEstimate BETWEEN ? AND ? AND District = ? AND County = ?' , (status, projectid, ConstructionCostEstimatefrom, ConstructionCostEstimateto, district, county))
        results = cur.fetchall();
        if len(results) == 0:
            flash('No Data available...')
        con.close()
        return render_template('sqldatabase.html', results=results)
    return render_template('sqldatabase.html', results=[])


@app.route('/configure',)
def configure():
    con = sql.connect("C:\\sqlite\\DOTConnections.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * from Config")
    results = cur.fetchall();
    con.close()
    return render_template('configure.html', results=results)

@app.route('/SaveFile', methods=['POST', 'GET'])
def SaveFile():
    if request.method == 'POST':
        configdata = request.form["hidden"]
        configdata = configdata.split("|")
        while('' in configdata) : 
            configdata.remove('')
        configdata = [configdata[i:i + 3] for i in range(0, len(configdata), 3)]
        configdata = pd.DataFrame(np.vstack(configdata))
        configdata.columns = ['Key Type','Key','Value'] 
        con = sql.connect("C:\\sqlite\\DOTConnections.db")
        configdata.to_sql('Config', con, if_exists='replace', index=False)
        con.close()

        con = sql.connect("C:\\sqlite\\DOTConnections.db")
        DOTConnections = pd.read_sql_query("SELECT * from DOT", con)
        Config = pd.read_sql_query("SELECT * from Config", con)
        con.close()

        Consolidate = pd.merge(DOTConnections, Config, how='left', left_on='Status', right_on='Key')
        Consolidate.drop(['Key Type', 'Key', 'StatusScore'], axis=1, inplace=True)
        Consolidate.rename(columns={'Value':'StatusScore'}, inplace=True)

        DOTConnections = Consolidate

        Consolidate = pd.merge(DOTConnections, Config, how='left', left_on='UrbanOrRuralFlag', right_on='Key')
        Consolidate.drop(['Key Type', 'Key', 'UrbanRuralScore'], axis=1, inplace=True)
        Consolidate.rename(columns={'Value':'UrbanRuralScore'}, inplace=True)

        DOTConnections = Consolidate

        Config.rename(columns={'Key':'ConstructionCostEstimate'}, inplace=True)
        ConfigureScore = Config[Config['Key Type'] == 'Cost Score']
        ConfigureScore.ConstructionCostEstimate = pd.to_numeric(ConfigureScore.ConstructionCostEstimate,errors = 'coerce')
        DOTConnections.ConstructionCostEstimate = pd.to_numeric(DOTConnections.ConstructionCostEstimate,errors = 'coerce')  
        ConfigureScore = ConfigureScore.sort_values(by=['ConstructionCostEstimate'])
        DOTConnections = DOTConnections.sort_values(by=['ConstructionCostEstimate'])
        Consolidate = pd.merge_asof(DOTConnections, ConfigureScore, on = 'ConstructionCostEstimate', direction = 'nearest')
        Consolidate.drop(['Key Type', 'CostScore'], axis=1, inplace=True)
        Consolidate.rename(columns={'Value':'CostScore'}, inplace=True)
        Config.rename(columns={'ConstructionCostEstimate':'Key'}, inplace=True)

        DOTConnections = Consolidate

        weightage = Config[Config['Key'] == 'Urban Score']
        Consolidate['Urban Score'] = int(weightage['Value'])

        weightage = Config[Config['Key'] == 'Status Score']
        Consolidate['Status Score'] = int(weightage['Value'])

        weightage = Config[Config['Key'] == 'Cost Score']
        Consolidate['Cost Score'] = int(weightage['Value'])

        Consolidate.drop(['CombinedScore'], axis=1, inplace=True)
        Consolidate[['StatusScore','Status Score']] = Consolidate[['StatusScore','Status Score']].astype(float)
        Consolidate[['CostScore','Cost Score']] = Consolidate[['CostScore','Cost Score']].astype(float)
        Consolidate[['UrbanRuralScore','Urban Score']] = Consolidate[['UrbanRuralScore','Urban Score']].astype(float)

        Consolidate['CombinedScore'] = Consolidate['StatusScore'] * Consolidate['Status Score'] + Consolidate['CostScore'] * Consolidate['Cost Score'] + Consolidate['UrbanRuralScore'] * Consolidate['Urban Score']

        Consolidate[['StatusScore','Status Score']] = Consolidate[['StatusScore','Status Score']].astype(int)
        Consolidate[['CostScore','Cost Score']] = Consolidate[['CostScore','Cost Score']].astype(int)
        Consolidate[['UrbanRuralScore','Urban Score']] = Consolidate[['UrbanRuralScore','Urban Score']].astype(int)
        Consolidate['CombinedScore'] = Consolidate['CombinedScore'].astype(int)

        Consolidate.drop(['Status Score', 'Cost Score', 'Urban Score'], axis=1, inplace=True)

        DOTConnections = Consolidate

        con = sql.connect("C:\\sqlite\\DOTConnections.db")
        DOTConnections.to_sql('DOT', con, if_exists='replace', index=False)
        con.close()
        flash('Changes for Scores updated successfully.')
        return redirect(url_for('configure'))
    return redirect(url_for('configure'))
        
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