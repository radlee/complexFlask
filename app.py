from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
# from data import Stories #Import Stories to get Access to returned dumy data
from flaskext.mysql import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from readCSVFile import readCSV

#Import pymysql for cursor to return a dictionary for selecting
#stories from the database
import pymysql
import csv

#Import fucntools for checking if users are looged in
from functools import wraps
app = Flask(__name__)

#Configure MySQL
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'Stories'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

#Initialize MySQL
mysql = MySQL(app)

#Variable  and equate it to the Storie's function returning stories data
# Stories = Stories()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/week1')
# @app.route('/week', methods=['GET', 'POST'])
def week1():
    # data = readCSV('static/files' + weekname + '.csv')
    data = readCSV('static/files/Week1.csv')
    return render_template('week.html', data=data)

@app.route('/week2')
def week2():
    data = readCSV('static/files/Week2.csv')
    return render_template('week.html', data=data)

@app.route('/week3')
def week3():
    data = readCSV('static/files/Week3.csv')
    return render_template('week.html', data=data)

@app.route('/week4')
def Week4():
    data = readCSV('static/files/Week4.csv')
    return render_template('week.html', data=data)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/stories')
def stories():

    #Create cursor that return Dictionary
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    #Get Stories
    result = cur.execute("SELECT * FROM stories")
    #This must be in a Dictionary form -- json
    stories = cur.fetchall()

    print stories

    if result > 0:
        return render_template('stories.html',stories=stories )
    else:
        msg = 'No Stories Found'
        return render_template('stories.html', msg=msg)
    #Close connection
    cur.close() #data

#Single Story
@app.route('/story/<string:id>/') # id = Dynamic Value
def story(id):
    #Create cursor that return Dictionary
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    #Get Stories
    result = cur.execute("SELECT * FROM stories WHERE id = %s", [id])
    #This must be in a Dictionary form -- json
    story = cur.fetchone()

    return render_template('story.html', story=story) #data


#WTForms ----------------
class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=50)])
    username = StringField("Username", [validators.Length(min=4, max=25)])
    email = StringField("Email", [validators.Length(min=6, max=50)])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords Do Not Match')
    ])
    confirm = PasswordField('Confirm Password')
# Register--------------
#Accept POST requests---
@app.route('/register', methods=['GET', 'POST'])
def register():
    #form variable
    form = RegisterForm(request.form)
    #Check what type of request ...POST or GET
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        #Encrypt Password before storing it
        password = sha256_crypt.encrypt(str(form.password.data))

        #Create the cursor
        conn = mysql.connect()
        cur = conn.cursor()

        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        #Commit to DB
        conn.commit()
        #Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get username and Passwords from the form--
        username = request.form['username']
        password_candidate = request.form['password']

        #Create a cursor
        conn = mysql.connect()
        cur = conn.cursor()

        #Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            #Get the stored hash
            data = cur.fetchone()
            password = data[4]

            #Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                print  "MATCHED"
                #Passed
                session['logged_in'] = True
                session['username'] = username

                flash("Login successfull", 'success')
                return redirect(url_for('dashboard'))

            else:
                error = "Invalid login"
                return render_template('login.html',error=error)
            #Close Connection
            cur.close()
        else:
            error = "Username not found"

    return render_template('login.html')

#Check if the User is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Login to view this page', 'danger')
            return redirect(url_for('login'))
    return wrap

#Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("Logged Out", 'success')
    return redirect(url_for('login'))


#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    #Create cursor that return Dictionary
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    #Get Stories
    result = cur.execute("SELECT * FROM stories")
    #This must be in a Dictionary form -- json
    stories = cur.fetchall()

    print stories

    if result > 0:
        return render_template('dashboard.html',stories=stories )
    else:
        msg = 'No Stories Found'
        return render_template('dashboard.html', msg=msg)
    #Close connection
    cur.close()

class StoryForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

#Add Story-----
@app.route('/add_story', methods=['GET', 'POST'])
@is_logged_in
def add_story():
    form = StoryForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # Create a cursor
        conn = mysql.connect()
        cur = conn.cursor()

        # Execute
        cur.execute("INSERT INTO stories(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

        #Commit
        conn.commit()

        #Close connection
        cur.close()
        flash('Stroy Created', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_story.html', form=form)

# Edit Story
@app.route('/edit_story/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_story(id):
    #Fill the form
    #Create cursor that return Dictionary
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # Get the story by id

    result = cur.execute("SELECT * FROM stories WHERE id = %s", [id])

    story = cur.fetchone()

    #Get the form
    form = StoryForm(request.form)

    #Populate story form fields
    form.title.data = story['title']
    form.body.data = story['body']

    if request.method == 'POST' and form.validate():

        title = request.form['title']
        body = request.form['body']

        #Create cursor that return Dictionary
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        # Execute
        cur.execute("UPDATE stories SET title=%s,body=%s WHERE id = %s", (title, body, id))

        #Commit
        conn.commit()

        #Close connection
        cur.close()
        flash('Story Updated', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_story.html', form=form)

#Delete Story
@app.route('/delete_story/<string:id>', methods=["POST"])
@is_logged_in
def delete_story(id):
    #Create cursor that return Dictionary
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    #Execute
    cur.execute("DELETE FROM stories WHERE id = %s", [id])
    #Commit
    conn.commit()

    #Close connection
    cur.close()
    flash('Story Deleted', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
