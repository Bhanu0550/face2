from flask import Flask
import os
import json, requests, subprocess, shlex
from flask import request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField
import json
from PIL import Image

class Config(object):
    SECRET_KEY = 'bhanu sai pratap'
    
app = Flask(__name__)
app.config.from_object(Config)


def execute_request():
    bashCommand = '''curl --request POST --url https://lambda-face-recognition.p.rapidapi.com/recognize 
    --header 'content-type: multipart/form-data' 
    --header 'x-rapidapi-host: lambda-face-recognition.p.rapidapi.com' 
    --header 'x-rapidapi-key: your_rapid_api_key' 
    --form albumkey=album_key
    --form album=ADMINS --form files=@photo.jpg'''

    args = shlex.split(bashCommand)
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    output, error = process.communicate()
    json_obj = json.loads(output)
    return json_obj

def check_confidence(json_obj):
    if json_obj['status'] == 'success':
        if len(json_obj['photos'][0]['tags']) == 0:
            return False
        confidence = json_obj['photos'][0]['tags'][0]['uids'][0]['confidence']
        flag = False
        if confidence > 0.5:
            flag = True
        return flag

class LoginForm(FlaskForm):
    username = StringField('Username')

@app.route('/', methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        file = request.files['file']
        image = Image.open(file)
        image.save('photo.jpg')

        json_obj = execute_request()
        flag = check_confidence(json_obj)

        if flag:
            return render_template('admin_panel.html', user=username)
        else:
            message = "Your photo was not recognized as admin's photo. Please, try again."
            login_form = LoginForm()
            return render_template('login_form.html', title='Login', form=login_form, message=message)

    return render_template('base.html', title='Login', form=login_form, message="")

@app.route('/login_form/', methods=['GET'])
def login_form():
    login_form = LoginForm()
    return render_template('login_form.html', title='Login', form=login_form, message="")
