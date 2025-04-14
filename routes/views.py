from flask import render_template, redirect, url_for, request, session, flash, send_file, jsonify, make_response
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, bcrypt, login_manager
import os
import pandas as pd
from models.user import User, UserFile
from routes.data_processing import get_attributes, process_data
from werkzeug.utils import secure_filename
from routes.vmodels.arima import forecast_with_arima
from routes.vmodels.prophet import forecast_with_prophet

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed_uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/dashboard')
@login_required
def dashboard():
    files = UserFile.query.filter_by(user_id=current_user.id).all()
     # ✅ Add this block to read processed files
    processed_folder = os.path.join(app.config['PROCESSED_FOLDER'], current_user.username)
    processed_files = []
    if os.path.exists(processed_folder):
        processed_files = os.listdir(processed_folder)
    forecasted_folder = os.path.join(app.root_path, 'forecasted_uploads', current_user.username)
    forecasted_files = []
    if os.path.exists(forecasted_folder):
        forecasted_files = [f for f in os.listdir(forecasted_folder) if f.endswith('.csv')]
    return render_template('NiceAdmin/index.html', files=files, processed_files=processed_files,forecasted_files=forecasted_files)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
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

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('NiceAdmin/pages-register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash("No file part!", "danger")
        return redirect(url_for('dashboard'))

    file = request.files['file']
    if file.filename == '':
        flash("No selected file!", "danger")
        return redirect(url_for('dashboard'))

    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
    os.makedirs(user_folder, exist_ok=True)
    file_path = os.path.join(user_folder, file.filename)
    file.save(file_path)

    new_file = UserFile(user_id=current_user.id, filename=file.filename)
    db.session.add(new_file)
    db.session.commit()

    flash("File uploaded successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    filename = secure_filename(filename)
    user_folder = os.path.join('forecasted_uploads', current_user.username)
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash("File not found!", "danger")
        return redirect(url_for('dashboard'))

@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    filename = secure_filename(filename)
    user_file = UserFile.query.filter_by(user_id=current_user.id, filename=filename).first()

    if not user_file:
        flash("Unauthorized or file not found!", "danger")
        return redirect(url_for('dashboard'))

    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(user_file)
    db.session.commit()

    flash(f'File "{filename}" deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/get_attributes')
@login_required
def fetch_attributes():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    response = get_attributes(filename, current_user.username)
    return jsonify(response)

@app.route('/process_data', methods=['POST'])
@login_required
def preprocess_data():
    try:
        data = request.json
        filename = data.get('filename')
        selected_columns = data.get('selected_columns', [])

        if not filename or not selected_columns:
            return jsonify({"error": "Filename and selected columns are required"}), 400

        processed_data = process_data(filename, current_user.username, selected_columns)
        return jsonify(processed_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/preview_data")
@login_required
def preview_data():
    filename = request.args.get("filename")
    file_path = os.path.join(PROCESSED_FOLDER, current_user.username, filename)

    try:
        df = pd.read_csv(file_path)
        preview = {
            "columns": df.columns.tolist(),
            "rows": df.head(5).fillna("").values.tolist()
        }
        return jsonify(preview)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/get_category_values_from_processed", methods=["POST"])
@login_required
def get_category_values_from_processed():
    data = request.json
    filename = data.get("filename")
    path = os.path.join(PROCESSED_FOLDER, current_user.username, filename)
    
    try:
        df = pd.read_csv(path)
        x_col = df.columns[0]  # Assuming first column is Category
        values = df[x_col].dropna().unique().tolist()
        return jsonify({"values": values})
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/get_categories/<filename>')
@login_required
def get_categories(filename):
    filepath = os.path.join(PROCESSED_FOLDER, current_user.username, filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    try:
        df = pd.read_csv(filepath)
        category_col = df.columns[0]  # Assuming 1st column is category
        categories = df[category_col].dropna().unique().tolist()
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/forecast', methods=['POST'])
@login_required
def forecast():
    print("Entered forecast function")
    data = request.get_json()
    filename = data['filename']
    category = data['category']
    model = data['model']
    forecast_period = int(data.get('forecast_period', 30)) 
    order_cost = int(data.get('order_cost', 60)) 
    holding_cost = int(data.get('holding_cost', 20) )
    filepath = os.path.join(PROCESSED_FOLDER, current_user.username, filename)
    
    if model == 'ARIMA':
        print("Entered")
        forecast_data = forecast_with_arima(filepath, category, current_user.username,forecast_period)
    elif model == 'Prophet':
        forecast_data = forecast_with_prophet(filepath, category, current_user.username,forecast_period,order_cost,holding_cost)
    else:
        return jsonify({'error': 'Invalid model selected'}), 400

    return jsonify({'forecast': forecast_data, 'eoq': forecast_data.get('eoq')})

@app.route('/forecast_visualize', methods=['POST'])
@login_required
def forecast_visualize():
    filename = request.form['filename']
    
    forecasted_folder = os.path.join('forecasted_uploads', current_user.username)
    file_path = os.path.join(forecasted_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'Forecasted file not found'}), 404

    try:
        df = pd.read_csv(file_path)
        df = df[['Date', 'Forecast']]  # Ensure correct columns
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

        return jsonify({
            'filename': filename,
            'data': [
                {'date': row['Date'], 'value': row['Forecast']}
                for index, row in df.iterrows()
            ]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500





