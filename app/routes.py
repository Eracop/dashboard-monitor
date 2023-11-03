from flask import render_template, url_for
from app import app
from app.forms import LoginForm, PostForm
from flask import render_template, flash, redirect
from flask_login import current_user, login_user
from app.models import User, Post
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from datetime import datetime
from app.forms import EditProfileForm
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
currentuser = None
if not firebase_admin._apps:
    current_directory = os.path.dirname(os.path.realpath(__file__))
    service_account_path = os.path.join(current_directory, 'serviceAccount.json')
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
    firebaseDb = firestore.client()

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Bao', "email": "test@email.com"}
    if currentuser is None:  # Use 'is' for comparison
        return render_template("index.html", title='METAL SYNTERING SYSTEM FOR AG POWDER IN MICRO SAMPLES', user=user)
    else:
        user = User.query.filter_by(username=current_user.username).first_or_404()  
 
    return render_template("index.html", title='METAL SYNTERING SYSTEM FOR AG POWDER IN MICRO SAMPLES', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global currentuser
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        currentuser = form.username.data
        login_user(user, remember=form.remember_me.data)
        next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    global currentuser
    currentuser = None
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # posts = [
    #     {'author': user, 'body': 'Test post #1'},
    #     {'author': user, 'body': 'Test post #2'}
    # ]
    posts = user.posts.all()
    form = PostForm()
    if form.validate_on_submit():
        p = Post(temp1=int(form.temp1.data), temp2=int(form.temp2.data), time1=int(form.time1.data), time2=int(form.time2.data), status=1, comment=form.comment.data, user_id=user.id)
        db.session.add(p)
        db.session.commit()
        print("ok")
        flash('Submit form successful!')
        next_page = url_for('user', username=current_user.username)
        return redirect(next_page)
    # return render_template('user.html', user=user, posts=posts)
    return render_template('user.html', user=user, form=form, posts=posts)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    global currentuser
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        currentuser = current_user.username
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/api/sinteringForm', methods=['POST'])
def submit():
    data = request.json  # Assumes data is sent in JSON format
    user_id = data.get('user_id')  # You may want to identify the user
    history_data = data.get('data')  # Data to be stored in Firebase


    print("history",data)
    history_ref = firebaseDb.collection('history')
    new_history_doc = history_ref.add(data)

    return jsonify({"message": "Data submitted successfully"})