# from flask import Flask, render_template, redirect, url_for, request, session, flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# from flask_bcrypt import Bcrypt
# import os
# from flask import send_file

# app = Flask(__name__)  
# app.config['SECRET_KEY'] = 'your_secret_key'

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Ensure the upload folder exists
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # Ensure the database folder exists
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_FOLDER = os.path.join(BASE_DIR, 'database')

# if not os.path.exists(DB_FOLDER):
#     os.makedirs(DB_FOLDER)

# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FOLDER}/users.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
# bcrypt = Bcrypt(app)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

# # User model for authentication
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)
# class UserFile(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     filename = db.Column(db.String(255), nullable=False)

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# # Function to create a personal database for each user
# def get_user_db(username):
#     return f"sqlite:///{DB_FOLDER}/{username}.db"

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         user = User.query.filter_by(username=username).first()
#         if user and bcrypt.check_password_hash(user.password, password):
#             login_user(user)
#             session['user_db'] = get_user_db(username)
#             return redirect(url_for('dashboard'))
        
#         flash("Invalid username or password!", "danger")
#         return redirect(url_for('login'))

#     return render_template('NiceAdmin/pages-login.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         username = request.form['username']
#         password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

#         if User.query.filter_by(username=username).first():
#             flash("Username already exists!", "danger")
#             return redirect(url_for('register'))

#         if User.query.filter_by(email=email).first():
#             flash("Email already registered!", "danger")
#             return redirect(url_for('register'))

#         new_user = User(name=name, email=email, username=username, password=password)
#         db.session.add(new_user)
#         db.session.commit()

#         # Create a separate database for the user
#         user_db_path = get_user_db(username)

#         user_app = Flask(__name__)
#         user_app.config['SQLALCHEMY_DATABASE_URI'] = user_db_path
#         user_db = SQLAlchemy(user_app)

#         class UserData(user_db.Model):
#             id = user_db.Column(user_db.Integer, primary_key=True)
#             data = user_db.Column(user_db.String(500))

#         with user_app.app_context():
#             user_db.create_all()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for('login'))

#     return render_template('NiceAdmin/pages-register.html')

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     user_db_path = session.get('user_db')
#     user_files = UserFile.query.filter_by(user_id=current_user.id).all()
#     user_app = Flask(__name__)
#     user_app.config['SQLALCHEMY_DATABASE_URI'] = user_db_path
#     user_db = SQLAlchemy(user_app)
#     class UserData(user_db.Model):
#         id = user_db.Column(user_db.Integer, primary_key=True)
#         data = user_db.Column(user_db.String(500))
#     with user_app.app_context():
#         user_data = UserData.query.all()
#     return render_template('NiceAdmin/index.html', data=user_data,files=user_files)

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     session.pop('user_db', None)
#     flash("Logged out successfully!", "success")
#     return redirect(url_for('home'))

# @app.route('/upload', methods=['POST'])
# @login_required
# def upload_file():
#     if 'file' not in request.files:
#         flash("No file part!", "danger")
#         return redirect(url_for('dashboard'))
#     file = request.files['file']
#     if file.filename == '':
#         flash("No selected file!", "danger")
#         return redirect(url_for('dashboard'))

#     user_folder = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
#     os.makedirs(user_folder, exist_ok=True)

#     # Save the file inside the user's folder
#     file_path = os.path.join(user_folder, file.filename)
#     file.save(file_path)

#     # Save file entry in the database
#     new_file = UserFile(user_id=current_user.id, filename=file.filename)
#     db.session.add(new_file)
#     db.session.commit()

#     flash("File uploaded successfully!", "success")
#     return redirect(url_for('dashboard'))

# @app.route('/download/<filename>')
# @login_required
# def download_file(filename):
#     user_folder = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
#     file_path = os.path.join(user_folder, filename)

#     if os.path.exists(file_path):
#         return send_file(file_path, as_attachment=True)
#     else:
#         flash("File not found!", "danger")
#         return redirect(url_for('dashboard'))
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         print("✅ User Database Created Successfully!")

#     app.run(debug=True)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os

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
        print("✅ User Database Created Successfully!")

    app.run(debug=True)

