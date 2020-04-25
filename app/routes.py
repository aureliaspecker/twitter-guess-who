import os
from app import app
from flask import render_template, flash, redirect
from app.forms import InputUsersForm
from .server.twitter_guess_who import TwitterGuessWho

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

tgw = TwitterGuessWho()

@app.route('/')

@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/setup',methods=['post','get'])
def setup():
    form = InputUsersForm()
    if form.validate_on_submit():
        if tgw.num_users == 6: 
            return redirect('/round1')
        else: 
            user_exists = tgw.add_user(form.username.data)
            if user_exists:
                flash('User added: {}'.format(tgw.users[-1]))
            else:
                flash('User does not exist: {}'.format(form.username.data))
            return redirect('/setup')
    return render_template('setup.html', title='Setup', form=form)

@app.route('/round1')
def round1():
    tgw.get_user_data()
    return render_template('round1.html', title='Round-1')