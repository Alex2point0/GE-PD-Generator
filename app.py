"""
General Electric PD Generator
(c) Oleg Khomenko
"""


import os
import json
from flask import Flask, render_template, request, redirect, url_for, request, session, flash, send_from_directory
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
UPLOAD_FOLDER = './static/uploaded'
ALLOWED_EXTENSIONS = set(['json'])


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
            if False:
                filename = secure_filename(file.filename)
            else:
                filename = 'data.json'
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.save(app.config['UPLOAD_FOLDER'] + '/' + filename)
            return redirect(url_for('uploaded_file',
                                    filename=filename))
        else:
            return render_template('upload.html', error="Cannot upload this file") 
    return render_template('upload.html', error=None)


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)



app.secret_key = 'ge pd generator'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.environ['USER'] = 'admin'
os.environ['PASS'] = 'admin'

@app.route('/')
def index():
    with open(app.static_folder + '/uploaded/data.json', 'r') as json_data:
        d = json.load(json_data)
    return render_template('index.html', data=d)


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


# This one is a test zone
@app.route('/test')
def test():
    data = None
    return render_template('test.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
