from flask import Flask, render_template, redirect, url_for, session, flash, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
import pymysql
import requests
import base64
from datetime import datetime
import json  

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def connect_to_database():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='db',
        cursorclass=pymysql.cursors.DictCursor
    )

def get_access_token():
    consumer_key = "ZXFRgG801YwWVTnS1YOA4p9LlVXdudNgJV8Pnf6SJ8zlOVOn"  
    consumer_secret = "SGILYZJtPJkNtIHuhtaiVxkEVaLno4YgN7yhak2PaGB1AFzIBBmgZAqXIKowb2AR"  
    access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)
    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status() 
        result = response.json()
        access_token = result['access_token']
        return {'access_token': access_token}
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        with connect_to_database().cursor() as cur:
            cur.execute("SELECT * FROM users where email=%s", (field.data,))
            user = cur.fetchone()
            if user:
                raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

@app.route('/')
def index():
    get_access_token()
    return render_template('home.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store data into database
        with connect_to_database().cursor() as cur:
            cur.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name, email, hashed_password))
            connect_to_database().commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        with connect_to_database().cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Please check your email and password")
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        with connect_to_database().cursor() as cur:
            cur.execute("SELECT * FROM users where id=%s", (user_id,))
            user = cur.fetchone()

        if user:
            return render_template('dashboard.html', user=user)

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('index'))


    
if __name__ == '__main__':
    app.run(debug=True)
