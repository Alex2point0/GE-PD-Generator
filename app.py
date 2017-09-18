'''
General Electric PD Generator
(c) Oleg Khomenko
'''


import os
import re
import json
from flask import Flask, render_template, request, redirect, url_for, request, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from functools import wraps
import pandas as pd
import numpy as np

app = Flask(__name__)


# Classes
class Question:
    def __init__(self):
        self.type = 'question_with_options'
        self.label = 'Label'
        self.options = ['Thanks for __', 'Body el2']


# Constants
UPLOAD_FOLDER = './static/uploaded'
ALLOWED_EXTENSIONS = set(['xlsx'])


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
                # We can use original name of the file
                filename = secure_filename(file.filename)
            else:
                # We replace name with data.json everytime
                filename = 'data.json'

            # First save
            file.save(app.config['UPLOAD_FOLDER'] + '/' + filename)

            # PANDAS
            # Now let's prepare file 
            df = pd.read_excel(app.config['UPLOAD_FOLDER'] + '/' + filename)
            df.columns = ['qID', 'Text', 'Parent']
            df.loc[:,'Label'] = 'Dummy'

            def prepare_json_from_xlsx(df):
                data = {}
                for i, q in enumerate(df.qID.unique()):
                    df.loc[df.qID == q,'Value'] = np.arange(df[df.qID == q].shape[0], dtype='int')
                    data[str(q)] = {
                        'Label': df.loc[df.qID == q, 'Label'].iloc[0],
                        'Num': i,
                        'Options': [{'Parent': row[2], 'Text': row[1], 'Value': row[4]}
                                    for row 
                                    in df.loc[df.qID == q].values]
                    }
                return data


            res = prepare_json_from_xlsx(df)
            
            with open(app.config['UPLOAD_FOLDER'] + '/' + filename, 'w') as outfile:
                json.dump(res, outfile)

            ## END PANDAS
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

### EC SELECTION
@app.route('/ecselection', methods=['GET', 'POST'])
def ecselection():
    NS = 1600
    ETA_EX = 85
    ETA_COMP = 75

    data = None
    if request.method == 'POST':
        data = request.form
        
        N = (37 * NS * float(data['deltaH'])**.75) / (data['Q_1'] ** 0.5)
        D2_ex = 5.6 * (10**5) * (float(data['deltaH']) ** .5) / N
        W = (float(data['G_ex']) * float(data['deltaH']) * ETA_EX) - 5
        deltaH_comp = W * ETA_COMP / float(data['G_comp'])
        D2_comp = 9 * 10**5 * deltaH_comp**.5 / N
        FI = 6.76 * 10**6 * float(data['Q_1']) / (N * D2_comp**3)
        data = [N, D2_ex, W, deltaH_comp, D2_comp, FI]

    return render_template('ecselection.html', data=data)

### -- EC SELECTION

@app.route('/roulette', methods=['GET', 'POST'])
def roulette():

    if request.method == 'GET':
        data = {}
        for i in range(10):
            data[i] = {
                'name': 'Person #' + str(i),
                'email': 'Email #' + str(i)
            }

    if request.method == 'POST':

        # Copy-pasted
        participants = request.form['participants']
        participants = participants.split(";")
        participants = [p for p in participants if '~CORP' not in p]
        
        data = {}
        for i, p in enumerate(participants):
            data[i] = {}
            
            # Parsing name
            name = re.search(r'.*\(', p)
            if name:
                data[i]['name'] = name.group()[:-1]
                
            # Parsing email
            email = re.search(r'<.+@.+>', p)
            if email:
                data[i]['email'] = email.group()[1:-1]

        # Adding Entered values to Data
        participants_entered = request.form['participants-entered']
        if participants_entered:
            participants_entered = participants_entered.split(",")
            for i in range(len(participants_entered) - 1):
                idx = i + len(data.keys())
                data[idx] = {}
                data[idx]['name'] = participants_entered[i]
                data[idx]['email'] = None

    return render_template('roulette.html', data=json.dumps(data))

if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    debug = os.getenv("FLASK_DEBUG")
    app.run(host='0.0.0.0', port=port, debug=debug)
