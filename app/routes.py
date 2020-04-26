import os
import sys
from app import app
from flask import render_template, flash, redirect
from app.forms import InputUsersForm, SelectFormList
from .server.twitter_guess_who import TwitterGuessWho

# Generate random secret key
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Initialise game object
tgw = TwitterGuessWho()


@app.route('/')


@app.route('/index')
def index():
    """
    Home page.
    """
    return render_template('index.html', title='Home')


@app.route('/setup',methods=['post','get'])
def setup():
    """
    Page to get user handles from player.
    """
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


@app.route('/round1',methods=['post','get'])
def round1():
    """
    First round of game.
    """

    # Make API calls for entire game in first round (check for rate limits etc.)
    tgw.make_api_calls()

    # Get data for this round
    users = tgw.get_users()
    num_users = len(users)
    tweet_counts, jumbled_users = tgw.get_tweet_counts(sort=True)

    # Generate forms
    form_list = construct_select_forms(users)

    # Get player answers
    if form_list.is_submitted():
        points = 0
        for i in range(num_users):
            if jumbled_users[i]==users[int(form_list.select_forms.data[i]['select'])]:
                points += 1
        flash('You scored {} points!'.format(points))
        return redirect('/round1')
    return render_template('round1.html', title='Round1', n=num_users, form_list=form_list, tweet_counts=tweet_counts)


def construct_select_forms(users):
    """
    Construct form with given number of select forms, each with given options.
    :return: form of list of select forms 
    """

    form_list = SelectFormList()
    for i in range(len(users)):
        form_list.select_forms.append_entry()
    for form in form_list.select_forms:
        form.select.choices = [(i,user) for i,user in enumerate(users)]

    return form_list
