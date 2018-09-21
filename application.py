from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, login_required, login_user, logout_user

from config import Config
from mockdbhelper import MockDBHelper as DBHelper
from models import User
from passwordhelper import PasswordHelper

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
    return render_template('index.html')


@app.route('/account')
@login_required
def account():
    return 'You are logged in!'


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    stored_user = DB.get_user(email)

    if stored_user and PH.validate_password(password, stored_user['salt'], stored_user['hashed']):
        user = User(email)
        login_user(user, remember=True)
        return redirect(url_for('account'))
    return index()


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=5000, debug=True)
