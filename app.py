# importing required libraries

import csv
import sqlite3
from datetime import date
from feature import FeatureExtraction
from flask import Flask, request, render_template, session, url_for, redirect
import numpy as np
import pandas as pd
from sklearn import metrics
import warnings
import pickle
import requests
warnings.filterwarnings('ignore')

today = date.today()
file = open("pickle/model.pkl", "rb")
gbc = pickle.load(file)
file.close()


app = Flask(__name__)
app.secret_key = 'mysecretkey'


@app.route('/user')
def user():
    if 'username' not in session:
        return render_template('error.html')
    return render_template("user.html")


@app.route('/gmail')
def gmail():
    return render_template('gmail.html')


@app.route("/gmail", methods=["POST"])
def info():
    if request.method == 'POST':
        email = request.form['email']
        api_key = 'YOUR_EMAILREP.IO_API_KEY'
        api_url = 'https://emailrep.io/' + email
        response = requests.get(api_url)
        data = response.json()
        return render_template('gmail.html', data=data)
    else:
        return render_template('gmail.html')
# index
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/',methods=['POST'])
def login():
    if request.method == 'POST':
        # get the entered username and password from the form
        username = request.form['username']
        password = request.form['password']

        # connect to the database and retrieve the password for the entered username
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", [username])
        result = cursor.fetchone()
        conn.close()

        # check if the password matches the entered password
        if result and result[0] == password:
            # set the username in the session and redirect to the dashboard page
            session['username'] = username
            return redirect(url_for('user'))
        else:
            # display an error message if the username or password is incorrect
            error = 'Invalid username or password'
            return render_template('index.html', error=error)
    else:
        # display the login page if no form data is submitted
        return render_template('index.html')

@app.route('/logout',methods=['POST'])
def logout():
    # remove the username from the session and redirect to the login page
    session.pop('username', None)
    return redirect(url_for('login'))
# user complaint page
@app.route('/complaint')
def complaint():
    return render_template("complaint.html")

# get user complaint
@app.route('/complaint', methods=['POST'])
def complaintwrite():
    email = request.form['user']
    msg = request.form['complaint']
    usercomplaint = f"\n{email},{msg}"
    with open('complaint.csv','a') as complaintfile:
        complaintfile.write(usercomplaint)
    return render_template('user.html',data="Complain Registered")

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if 'username' not in session:
        return render_template('error.html')
    if request.method == "POST":

        url = request.form["url"]
        data = f'{url},{today} \n'
        with open('data.csv',"a") as csvfile:
            csvfile.write(data)
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1,30) 

        y_pred =gbc.predict(x)[0]
        #1 is safe       
        #-1 is unsafe
        y_pro_phishing = gbc.predict_proba(x)[0,0]
        y_pro_non_phishing = gbc.predict_proba(x)[0,1]
        # if(y_pred ==1 ):
        pred = "It is {0:.2f} % safe to go ".format(y_pro_phishing*100)
        return render_template('submit.html',xx =round(y_pro_non_phishing,2),url=url )
    return render_template("submit.html", xx =-1)

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin",methods=["POST"])
def adminpost():
    username = request.form['username']
    password = request.form['password']
    connect = sqlite3.connect('login.db')
    cursor=connect.cursor()
    user_data=[(username,password)]
    # read user csv file
    with open('data.csv','r') as f:
        data=[tuple(line) for line in csv.reader(f)]
        table=tuple(data)
    # read  user complaints
    with open('complaint.csv') as file:
        eachcomplaint = [tuple(line) for line in csv.reader(file)]
        complaintdata = tuple(eachcomplaint)
        # play with db
    data=cursor.execute(''' SELECT * FROM LOGIN''')
    for row in data:
        row=[row]
        if row == user_data:
            return render_template("Dashboard.html",table=table,complaintdata=complaintdata)
        else :
            return render_template('admin.html',message="Wrong Username Or Password")

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")
