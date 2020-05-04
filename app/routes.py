import os
import sys
import json
from app import app
from flask import render_template, flash, redirect
from app.forms import InputUsersForm, SelectFormList
from .server.twitter_guess_who import TwitterGuessWho
from .server.api_handler import Random_Gif

# Generate random secret key
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Initialise GIPHY API
random_gif = Random_Gif(authentication_key=os.getenv('GIPHY_KEY'))

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
    return render_template('setup.html', title='Setup', form=form, next_page=f"/round{tgw.next_round}")


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
        tgw.update_score(points)
        tgw.next_round += 1
        return redirect('/score')
    return render_template('round1.html', title='Round1', n=num_users, form_list=form_list, tweet_counts=tweet_counts)


@app.route('/round2', methods=['post', 'get'])
def round2():
    """
    Second round of the game.
    """

    # Get data for this round
    users = tgw.get_users()
    num_users = len(users)
    user_bios, jumbled_users = tgw.get_user_bio(seed=0)

    #Generate forms
    form_list = construct_select_forms(users)

    # Get player answers
    if form_list.is_submitted():
        points = 0
        for i in range(num_users):
            player_answer = users[int(form_list.select_forms.data[i]['select'])][1:]
            correct_answer = jumbled_users[i]
            if correct_answer==player_answer:
                points += 1
        tgw.update_score(points)
        tgw.next_round += 1
        return redirect('/score')
    return render_template('round2.html', title='Round2', n=num_users, form_list=form_list, user_bios=user_bios)


@app.route('/round3', methods=['post', 'get'])
def round3():
    """
    Third round of the game.
    """

    # Get data for this round
    users = tgw.get_users()
    num_users = len(users)
    wordcloud_paths = tgw.make_user_wordclouds()

    # Generate forms
    form_list = construct_select_forms(users)

    # # Get player answers
    # if form_list.is_submitted():
    #     points = 0
    #     for i in range(num_users):
    #         player_answer = users[int(form_list.select_forms.data[i]['select'])][1:]
    #         correct_answer = jumbled_users[i]
    #         if correct_answer==player_answer:
    #             points += 1
    #     tgw.update_score(points)
    #     tgw.next_round += 1
    #     return redirect('/score')
    return render_template('round3.html', title='Round3', n=num_users, form_list=form_list, wc_paths = wordcloud_paths)


@app.route('/score', methods=['get'])
def score():
    """
    Displays score
    """

    # Get player score and total possible score
    score = tgw.get_score()
    max_score = tgw.num_users*(tgw.next_round-1)

    # Generate gif based on result
    if score>0:
        relative_score = score/max_score
    else:
        relative_score = 0
    gif_tags = ['disaster','bad','ok','awesome','epic'] # 0,0.25,0.5,0.75,1.0
    gif_url = json.loads(random_gif(tags=gif_tags[int(relative_score/0.25)]).text)['data']['fixed_height_downsampled_url']
    return render_template('score.html', score=score, max_score=max_score, next_page=f"/round{tgw.next_round}", gif_url=gif_url)


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


