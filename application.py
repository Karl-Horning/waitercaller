from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from config import Config
from forms import LoginForm, RegistrationForm
from mockdbhelper import MockDBHelper as DBHelper
from models import User
from passwordhelper import PasswordHelper

import datetime

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
login_manager = LoginManager(app)

DB = DBHelper()
PH = PasswordHelper()


@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)


@app.route('/')
def index():
    registrationform = RegistrationForm()
    return render_template('index.html', loginform=LoginForm(), registrationform=RegistrationForm())


@app.route('/register', methods=['POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate():
        if DB.get_user(form.email.data):
            form.email.errors.append('Email address already registered')
            return render_template('index.html', loginform=LoginForm(), registrationform=form)
        salt = PH.get_salt()
        hashed = PH.get_hash(form.password2.data + salt)
        DB.add_user(form.email.data, salt, hashed)
        return render_template('index.html', loginform=LoginForm(), registrationform=form, onloadmessage='Registration successful. Please log in.')
    return render_template('index.html', loginform=LoginForm(), registrationform=form)


@app.route('/login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():
        stored_user = DB.get_user(form.loginemail.data)
        if stored_user and PH.validate_password(form.loginpassword.data, stored_user['salt'], stored_user['hashed']):
            user = User(form.loginemail.data)
            login_user(user, remember=True)
            return redirect(url_for('account'))
        form.loginemail.errors.append('Email or password invalid')
    return render_template('index.html', loginform=form, registrationform=RegistrationForm())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    now = datetime.datetime.now()
    requests = DB.get_requests(current_user.get_id())
    for req in requests:
        deltaseconds = (now - req['time']).seconds
        req['wait_minutes'] = f'{deltaseconds / 60}.{str(deltaseconds % 60).zfill(2)}'
    return render_template('dashboard.html', requests=requests)


@app.route('/dashboard/resolve')
@login_required
def dashboard_resolve():
    request_id = request.args.get('request_id')
    DB.delete_requests(request_id)
    return redirect(url_for('dashboard'))


@app.route('/account')
@login_required
def account():
    tables = DB.get_tables(current_user.get_id())
    return render_template('account.html', tables=tables)


@app.route('/account/createtable', methods=['POST'])
@login_required
def account_createtable():
    tablename = request.form.get('tablenumber')
    tableid = DB.add_table(tablename, current_user.get_id())
    new_url = Config.BASE_URL + 'newrequest/' + tableid
    DB.update_table(tableid, new_url)
    return redirect(url_for('account'))


@app.route('/account/deletetable')
@login_required
def account_deletetable():
    tableid = request.args.get('tableid')
    DB.delete_table(tableid)
    return redirect(url_for('account'))


@app.route('/newrequest/<tid>')
def new_request(tid):
    DB.add_request(tid, datetime.datetime.now())
    return 'Your request has been logged and a waiter will be with you shortly'


if __name__ == '__main__':
    app.run(port=5000, debug=True)
