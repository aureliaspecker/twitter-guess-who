from app import app
from flask import render_template, flash, redirect
from app.forms import InputUsersForm
import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')

@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/setup',methods=['post','get'])
def setup():
    form = InputUsersForm()
    if form.validate_on_submit():
        flash('XXX {}'.format(form.username.data))
        return redirect('/setup')
    return render_template('setup.html', title='Setup', form=form)


@app.route('/round1')
def round1():
    return render_template('round1.html', title='Round-1')