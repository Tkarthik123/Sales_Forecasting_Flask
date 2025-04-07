from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_FOLDER = os.path.join(BASE_DIR, 'database')

if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FOLDER}/users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Import models and routes
from routes.views import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

