from flask import Flask, request, redirect, render_template
import sys
from os import environ

app = Flask(__name__, template_folder='templates')

@app.route('/') 
def sql_database():
    from functions.sqlquery import sql_query
    results = sql_query(''' SELECT * FROM DOT''')
    msg = 'SELECT * FROM DOT'
    return render_template('sqldatabase.html', results=results, msg=msg)   


if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)