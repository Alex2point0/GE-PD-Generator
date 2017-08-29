"""
General Electric PD Generator
(c) Oleg Khomenko
"""


import os
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, request, session, flash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)

# Classes
class Question:
    def __init__(self):
        self.type = None
        self.label = 'Label'
        self.options = ['Body el1', 'Body el2']

# Functions
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return render_template(url_for('login'))
    return wrap

UPLOAD_FOLDER = '/static'
app.secret_key = 'ge pd generator'

os.environ['USER'] = 'admin'
os.environ['PASS'] = 'admin'
data = [Question() for _ in range(5)]

@app.route('/')
def index():
    return render_template('index.html', data=data)


@app.route('/login', methods=['GET', 'POST']) 
def login():
    error = None
    if request.method == 'POST':
        if request.form['user'] != os.getenv('USER') or request.form['pass'] != os.getenv('PASS'):
            error = 'Invalid credentials. Please Try again'
        else:
            print("User {} logon..".format(request.form['user']))
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
