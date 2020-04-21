from app import app
from flask import render_template

@app.route('/')

@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/round1')
def round1():
    return render_template('round1.html', title='Round-1')