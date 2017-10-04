'''
General Electric PD Generator
(c) Oleg Khomenko
'''


import os
import re
import json
import csv
import datetime 
from flask import Flask, render_template, request, redirect, url_for, request, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from functools import wraps
import pandas as pd
import numpy as np

app = Flask(__name__)


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

            def prepare_json_from_xlsx(d):
                sep_idx = d[d['QuestionID'] == 'SEPARATOR'].index[0]
                labels = d[d.index < sep_idx].set_index('QuestionID').Text
                d = d[d.index > sep_idx]
                
                data = {}
                for i, q in enumerate(d.QuestionID.unique()):
                    d.loc[df.QuestionID == q,'Value'] = np.arange(d[d.QuestionID == q].shape[0], dtype='int')
                    data[str(q)] = {
                        'Label': labels[q],
                        'Num': i,
                        'Options': [
                            {'Parent': row[1], 'Text': row[0], 'Value': row[2], 'Hashtag': row[3]}
                            for row in d.loc[d.QuestionID == q].values]
                        }
                        
                return data

            res = prepare_json_from_xlsx(df)
            
            # Save
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

@app.route('/save', methods=['POST'])
def save():
    try: # Trying open request
        data = request.form
        personFrom = data['personFrom']
        personTo = data['personTo']
        participants = data.getlist('participants[]')
        sso = data['sso']
    except Exception as e:
        print(e)
        return json.dumps({'success':False, 'error': 'couldnt parse data'}), 400, {'ContentType':'application/json'}

    try: # Trying write csv-file to store results
        with open(app.config['UPLOAD_FOLDER'] + '/' + 'roulette.csv', 'a', newline='') as f:
            csvwriter = csv.writer(f, delimiter=',')
            print(participants)
            csvwriter.writerow([datetime.datetime.now(), personFrom, personTo, sso, "\t".join(participants)])
            print("Results were saved\t",[datetime.datetime.now(), personFrom, personTo, sso, "\t".join(participants)])
    except Exception as e:
        print(e)
        return json.dumps({'success':False, 'error': 'couldnt save data'}), 400, {'ContentType':'application/json'}

    return json.dumps({'success':True,}), 200, {'ContentType':'application/json'}



# Roulette
@app.route('/roulette', methods=['GET', 'POST'])
def roulette():

    if request.method == 'GET':
        data = {}
        scroll = None
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

        participants_selected = request.form.getlist('participants-selected')
        print(participants_selected)
        
        data = {}
        if participants_selected:
            for i in range(len(participants_selected)):
                data[i] = {}
                data[i]['name'] = participants_selected[i]
                data[i]['email'] = None
                scroll = 'secondPage'
        else:
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

    return render_template('roulette.html', data=json.dumps(data), scroll=scroll)

if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    debug = os.getenv("FLASK_DEBUG")
    app.run(host='0.0.0.0', port=port, debug=debug)
