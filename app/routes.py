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
import numpy as np
from matplotlib import pyplot as plt
import os
from io import BytesIO
import base64
from flask import send_file
from firebase_admin import db as realtimeDB

def generate_plot(temperature1, temperature2, duration1, duration2, pressure):
    # Define the limit of parameters
    maxtemperature = 400  # (degree Celsius)
    maxtime = 150  # (minutes)
    maxpressure = 5  # (MPa)

    # Calculate durationtemp
    durationtemp = duration1 * (temperature1 / temperature2)

    # Create time for temperature
    time12 = np.linspace(0, duration2, 1000)
    time3 = np.linspace(duration2, 130, 1000)

    # Create time for pressure
    ptime = np.linspace(0, maxtime, 1000)

    # Create temperature function
    temperature12_func = np.piecewise(time12, [time12 < duration1, (time12 >= duration1) & (time12 <= duration2)],
                                      [lambda t: temperature2 / duration1 * t, temperature2])
    temperature3_func = np.piecewise(time3, [time3 >= duration2], [lambda t: -temperature2 / (maxtime - duration2) * (t - duration2) + temperature2])

    # Create pressure function
    pressure_func = np.piecewise(ptime, [ptime < durationtemp, (ptime >= durationtemp) & (ptime <= duration2),
                                        (ptime >= duration2) & (ptime <= maxtime)],
                                [0, pressure, 0])

    # Initialize a matplotlib "figure"
    fig, ax1 = plt.subplots()
    ax1.set_facecolor("black")

    # Set labels for axes and plot temperature
    color = 'white'
    ax1.set_xlabel('Time (minutes)')
    ax1.set_xlim(0, maxtime)
    ax1.set_ylabel('Temperature (°C)', color="black")
    ax1.set_ylim(0, maxtemperature)

    # Plot temperature
    ax1.plot(time12, temperature12_func, color=color)
    ax1.plot(time3, temperature3_func, color=color, linestyle='dashed')
    ax1.tick_params(axis='y', labelcolor="black")

    # Highlight specific points for temperature
    ax1.plot([duration1, duration1], [0, temperature2], color=color, linestyle='dashed')
    ax1.plot([duration2, duration2], [0, temperature2], color=color, linestyle='dashed')
    ax1.plot([0, duration1], [temperature2, temperature2], color=color, linestyle='dashed')
    ax1.plot([0, durationtemp], [temperature1, temperature1], color=color, linestyle='dashed')

    # Add text labels at specific points in temperature
    ax1.text(duration1, 0, f'{duration1}', ha='left', va='bottom', color=color)
    ax1.text(duration2, 0, f'{duration2}', ha='left', va='bottom', color=color)
    ax1.text(0, temperature2, f'{temperature2}', ha='left', va='bottom', color=color)
    ax1.text(0, temperature1, f'{temperature1}', ha='left', va='bottom', color=color)

    # Create a new set of axes for pressure
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Pressure (MPa)', color=color)
    ax2.set_ylim(0, maxpressure)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.plot(ptime, pressure_func, color=color)
    fig.tight_layout()

    # Highlight specific points for pressure
    ax2.plot([duration2, maxtime], [pressure, pressure], color=color, linestyle='dashed')

    # Add text labels at specific points in pressure
    ax2.text(maxtime, pressure, f'{pressure}', ha='right', va='bottom', color=color)

    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)

    # Convert the plot to a base64 encoded image
    plot_image = base64.b64encode(buffer.read()).decode()
    return plot_image


currentuser = None
app2 = None
if not firebase_admin._apps:
    current_directory = os.path.dirname(os.path.realpath(__file__))
    service_account_path = os.path.join(current_directory, 'serviceAccount.json')
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
    firebaseDb = firestore.client()
    realtimeDb = os.path.join(current_directory, 'realTimeParam.json')
    realtimeDbCred = credentials.Certificate(realtimeDb)
    app2 = firebase_admin.initialize_app(realtimeDbCred, {
    'databaseURL': 'https://esp8266demo1-e43a5-default-rtdb.asia-southeast1.firebasedatabase.app'
    }, name='second_admin_instance')
    realtimeDatabase = realtimeDB.reference('restricted_access  /secret_document',app2)

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
    time_submit = data.get('time_submit')

    history_ref = firebaseDb.collection('history')

    # Create a new collection named after the user's ID if it doesn't exist
    user_collection = history_ref.document(user_id)  # Use user_id as the document name 
    user_collection.set({})  # Create an empty document if it doesn't exist

    new_record = user_collection.collection(time_submit).document()
    new_record.set(history_data, merge=True) 

    ref = realtimeDB.reference('/input', app2)
    ref.update(history_data)
    return jsonify({"message": "Data submitted successfully"})

@app.route('/api/history/<user_id>', methods=['GET'])
def get_user_data(user_id):
    # Ensure user_id is not empty or invalid
    if not user_id:
        return jsonify({"error": "Invalid user_id"}), 400


    history_ref = firebaseDb.collection('history').document(user_id)
    collections = history_ref.collections()
    documents_list = []
    
    for collection_ref in collections:
        for doc_ref in collection_ref.list_documents():
            documents_list.append(doc_ref.get().to_dict())
    
    return jsonify(documents_list)

@app.route('/generate_plot', methods=['GET'])
def generate_plot_api():
    # Get input parameters from the query string
    temperature1 = float(request.args.get('temperature1', 225))
    temperature2 = float(request.args.get('temperature2', 285))
    duration1 = float(request.args.get('duration1', 30))
    duration2 = float(request.args.get('duration2', 90))
    pressure = float(request.args.get('pressure', 1.5))

    # Generate the plot
    plot_image = generate_plot(temperature1, temperature2, duration1, duration2, pressure)

    # Return the plot image as a response
    return send_file(BytesIO(base64.b64decode(plot_image)), mimetype='image/png')

@app.route('/api/real-time-param', methods=['GET'])
def fetch_data():
    try:
        # Reference the specific location in your Firebase Realtime Database
        ref = realtimeDB.reference('/output', app2)
        print(ref.get())
        # Fetch the data from the reference
        data = ref.get()

        # Return the data as JSON
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})