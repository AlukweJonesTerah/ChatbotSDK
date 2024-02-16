from flask import Flask, render_template, redirect, url_for, session, flash, request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
import pymysql
from scripts.database_setup import setup_database
from scripts.auto_create import create_project_structure
from flask import Flask, render_template, request
import random
import json
from keras.models import load_model
import webbrowser
import numpy as np
import pickle
from nltk.stem import WordNetLemmatizer
import nltk
import os
from werkzeug.utils import secure_filename

nltk.download('popular', quiet=True)

setup_database()
# create_project_structure('./apikey.json', '1234')



app = Flask(__name__)


app.secret_key = os.urandom(24)

connection=pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='chatbotsdk_user'
)



class RegisterForm(FlaskForm):
    name = StringField("Name",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self,field):
        cur = connection.cursor()
        cur.execute("SELECT * FROM users where email=%s",(field.data,))
        user = cur.fetchone()
        cur.close()
        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Login")


# file file_upload logic
UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/setup_page')
def setup_page():
    return render_template('setup_page.html')

@app.route('/model_setup')
def model_setup():
    return render_template('cards_models.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/model_setup/file_upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        try:
            # Check if API key is provided
            if not api_key:
                flash('API key is required')
                return redirect(request.url)
        
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(filepath):
                    flash('File already exists')
                    return redirect(request.url)
                file.save(filepath)
                # Check if the file is empty
                if os.path.getsize(filepath) == 0:
                    flash('The selected file is empty')
                    os.remove(filepath)  # Remove the empty file
                    return redirect(request.url)
                return redirect(url_for('download_file', name=filename))
        except (FileExistsError, PermissionError, IOError, ValueError) as e:
            # Handle specific exceptions
            flash(f'An error occurred: {str(e)}')
            return redirect(request.url)
        except Exception as e:
            # Handle any other unexpected exceptions
            flash(f'An unexpected error occurred: {str(e)}')
            return redirect(request.url)
    # For GET requests or invalid POST requests, render the file upload form
    return render_template('file_upload_form.html')





@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

        # store data into database 
        cur = connection.cursor()
        cur.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",(name,email,hashed_password))
        connection.commit()
        cur.close()

        return redirect(url_for('login'))

    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cur = connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cur.fetchone()
        cur.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Please check your email and password")
            return redirect(url_for('login'))

    return render_template('login.html',form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        cur = connection.cursor()
        cur.execute("SELECT * FROM users where id=%s",(user_id,))
        user = cur.fetchone()
        cur.close()

        if user:
            return render_template('dashboard.html',user=user)
            
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('index'))



# trial chatbot


lemmatizer = WordNetLemmatizer()
model = load_model('./chatbots/Councellor/model.counsellor')
intents = json.loads(open('./chatbots/Councellor/data.json', "r+", encoding="utf-8").read())
words = pickle.load(open('./chatbots/Councellor/texts.pkl', 'rb'))
classes = pickle.load(open('./chatbots/Councellor/labels.pkl', 'rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(
        word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence


def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return(np.array(bag))


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag'] == tag):
            result = random.choice(i['responses'])
            break
    return result


def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res






@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chatbot_response(userText)

if __name__ == '__main__':
    app.run(debug=True, host='*', port=8000)
