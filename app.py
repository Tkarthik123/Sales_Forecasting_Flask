from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('NiceAdmin/pages-login.html')

@app.route('/register')
def register():
    return render_template('NiceAdmin/pages-register.html')

@app.route('/data')
def data_page():
    return render_template('tables-data.html')

if __name__ == '__main__':
    app.run(debug=True)
