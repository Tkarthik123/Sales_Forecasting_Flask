from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)  
app.config['SECRET_KEY'] = 'your_secret_key'

# Ensure the database folder exists
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

# User model for authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Function to create a personal database for each user
def get_user_db(username):
    return f"sqlite:///{DB_FOLDER}/{username}.db"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            session['user_db'] = get_user_db(username)
            return redirect(url_for('dashboard'))
        
        flash("Invalid username or password!", "danger")
        return redirect(url_for('login'))

    return render_template('NiceAdmin/pages-login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for('register'))

        new_user = User(name=name, email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Create a separate database for the user
        user_db_path = get_user_db(username)

        user_app = Flask(__name__)
        user_app.config['SQLALCHEMY_DATABASE_URI'] = user_db_path
        user_db = SQLAlchemy(user_app)

        class UserData(user_db.Model):
            id = user_db.Column(user_db.Integer, primary_key=True)
            data = user_db.Column(user_db.String(500))

        with user_app.app_context():
            user_db.create_all()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('NiceAdmin/pages-register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_db_path = session.get('user_db')

    user_app = Flask(__name__)
    user_app.config['SQLALCHEMY_DATABASE_URI'] = user_db_path
    user_db = SQLAlchemy(user_app)

    class UserData(user_db.Model):
        id = user_db.Column(user_db.Integer, primary_key=True)
        data = user_db.Column(user_db.String(500))

    with user_app.app_context():
        user_data = UserData.query.all()

    return render_template('NiceAdmin/index.html', data=user_data)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_db', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ User Database Created Successfully!")

    app.run(debug=True)
