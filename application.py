from flask import Flask, render_template
from flask_login import LoginManager, login_required

app = Flask(__name__)
login_manager = LoginManager(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/account')
@login_required
def account():
    return 'You are logged in!'

if __name__ == '__main__':
    app.run(port=5000, debug=True)