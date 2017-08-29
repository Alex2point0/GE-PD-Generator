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
        self.type = 'question_with_options'
        self.label = 'Label'
        self.options = ['Thanks for __', 'Body el2']

# Constants
UPLOAD_FOLDER = '/static'
ALLOWED_EXTENSIONS = set(['csv'])


# Functions
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect('/')
    return wrap


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
        else:
            return render_template('upload.html', error="Cannot upload this file") 
    return render_template('upload.html', error=None)
    

app.secret_key = 'ge pd generator'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
