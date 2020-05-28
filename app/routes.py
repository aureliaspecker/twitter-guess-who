import os
import json
import shortuuid
from app import app
from flask import render_template, flash, redirect, request, session
from app.forms import InputUsersForm, SelectFormList
from .server.authentication import Authentication
from .server.twitter_guess_who import TwitterGuessWho
from .server.api_handler import Search_Gif


# Setup auth and security
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Initialise GIPHY API
search_gif = Search_Gif(authentication_key=os.getenv('GIPHY_KEY'))

# Initialise database of player authentications and games
player_auths = {}
player_games = {}


@app.route('/')


@app.route('/index')
def index():
    """
    Home page.
    """

    # try:
    # Start new session
    player_id = shortuuid.uuid()
    auth = Authentication()
    signin = auth.get_sign_in_url()
    session['player_id'] = player_id
    player_auths[player_id] = auth
    return render_template('index.html', title='Home', sign_in_url=signin)
    # except:
    #     return redirect('/error')


@app.route('/start', methods=['post', 'get'])
def start():
    """
    Callback to redirect user with Sign-In-With-Twitter.
    """

    # try:
    # Get oauth_token and oauth_verifer for SIWT and generate user tokens
    player_id = session['player_id']
    auth = player_auths[player_id]
    auth.generate_user_tokens(request.full_path)
    player_games[player_id] = TwitterGuessWho(auth)
    return render_template('start.html', player_name=auth.SCREEN_NAME)
    # except:
    #     return redirect('/error')


@app.route('/setup',methods=['post','get'])
def setup():
    """
    Page to get user handles from player.
    """

    # try:
    player_id = session['player_id']
    tgw = player_games[player_id]
    form = InputUsersForm()
    if form.validate_on_submit():
        if tgw.num_users == 6: 
            return redirect('/round1')
        else: 
            user_code = tgw.add_user(form.username.data)
            if user_code == 0:
                flash('User added')
            elif user_code == 1:
                flash('User already added: {}'.format(form.username.data))
            else:
                flash('User does not exist: {}'.format(form.username.data))
            flash('Users: '+', '.join(tgw.get_users()))
            return redirect('/setup')
    return render_template('setup.html', form=form, next_page="/play", num_users=tgw.num_users)
    # except: 
    #     return redirect('/error')


@app.route('/play',methods=['post','get'])
def fetch_data():
    """
    Make API calls and fetch Twitter data for users.
    """

    # try:
    # Make API calls for entire game in first round (check for rate limits etc.)
    player_id = session['player_id']
    tgw = player_games[player_id]
    api_call_successful, status_code = tgw.make_api_calls()
    if not api_call_successful:
        return redirect('/error')
    gif_url = "https://media.giphy.com/media/VgSjnwSoqiPjRRIJ1F/giphy.gif"
    return render_template('play.html', gif_url=gif_url, next_page=f"/round{tgw.next_round}")
    # except:
    #     return redirect('/error')


@app.route('/round1',methods=['post','get'])
def round1():
    """
    First round of game: Tweet counts.
    """

    # try:
    # Get data for this round
    player_id = session['player_id']
    tgw = player_games[player_id]
    tweet_counts, users = tgw.get_tweet_counts(sort=False)
    sorted_tweets, sorted_users = tgw.get_tweet_counts(sort=True)
    num_users = len(users)

    # Generate forms
    form_list = construct_select_forms(users)

    # Get player answers
    if form_list.is_submitted():
        points = 0
        for i in range(num_users):
            if sorted_tweets[i] == tweet_counts[int(form_list.select_forms.data[i]['select'])]:
                points += 1
        tgw.update_score(points)
        tgw.next_round += 1
        return redirect('/score')
    return render_template('round1.html', n=num_users, form_list=form_list, tweet_counts=sorted_tweets)
    # except: 
    #     return redirect('/error')


@app.route('/round2', methods=['post', 'get'])
def round2():
    """
    Second round of the game: Twitter bios.
    """

    # try: 
    # Get data for this round
    player_id = session['player_id']
    tgw = player_games[player_id]
    users = tgw.get_users()
    num_users = len(users)
    user_bios, jumbled_users = tgw.get_user_bio()

    # Generate forms
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
    return render_template('round2.html', n=num_users, form_list=form_list, user_bios=user_bios)
    # except: 
    #     return redirect('/error')


@app.route('/round3', methods=['post', 'get'])
def round3():
    """
    Third round of the game: Tweet wordclouds.
    """

    # try:
    # Get data for this round
    player_id = session['player_id']
    tgw = player_games[player_id]
    users = tgw.get_users()
    num_users = len(users)
    wordcloud_paths = tgw.get_wordcloud_paths()

    # Randomise order
    shuffle = tgw.get_shuffle()
    wordcloud_shuffle = [wordcloud_paths[i] for i in shuffle]

    # Generate forms
    form_list = construct_select_forms(users)

    # Get player answers
    if form_list.is_submitted():
        points = 0
        for i in range(num_users):
            player_answer = wordcloud_paths[int(form_list.select_forms.data[i]['select'])]
            correct_answer = wordcloud_shuffle[i]
            # Compare wordcloud paths instead of users
            # Allows default wordclouds to evaluate as correct regardless of order
            if correct_answer==player_answer:
                points += 1
        tgw.update_score(points)
        tgw.next_round += 1
        return redirect('/score')
    return render_template('round3.html', n=num_users, form_list=form_list, wc_paths = wordcloud_shuffle)
    # except: 
    #     return redirect('/error')


@app.route('/error', methods=['get'])
def error():
    """
    Notifies user of an error if the API call was unsuccessful.
    """

    # try:
    player_id = session['player_id']
    player_auths.pop(player_id)
    tgw = player_games.pop(player_id)
    tgw.clear_data_files()
    # except:
    #     pass
    return render_template('error.html',next_page="/index",)


@app.route('/score', methods=['get'])
def score():
    """
    Displays score.
    """

    # try: 
    # Get player score and total possible score
    player_id = session['player_id']
    tgw = player_games[player_id]
    score = tgw.get_score()
    rounds_played = tgw.next_round - 1
    max_score = tgw.num_users*rounds_played
    random_gif_id = tgw.get_uniform_random_integer()

    # Generate gif based on result
    if score>0:
        relative_score = score/max_score
    else:
        relative_score = 0
    gif_tags = ['disaster','disappointing','mediocre','congrats','awesome'] # 0,0.25,0.5,0.75,1.0
    try:
        gifs = search_gif(query=gif_tags[int(relative_score/0.25)],limit=40)
        gif_url = json.loads(gifs.text)['data'][random_gif_id]['images']['fixed_height']['url']
    except:
        gif_url = 'https://media.giphy.com/media/eYilisUwipOEM/giphy.gif'
    return render_template('score.html', score=score, max_score=max_score, next_page=f"/round{tgw.next_round}", gif_url=gif_url)
    # except: 
    #     return redirect('/error')


@app.route('/round4', methods=['get'])
def goodbye():
    """
    Closing page.
    """

    # try:
    player_id = session['player_id']
    player_auths.pop(player_id)
    tgw = player_games.pop(player_id)
    tgw.clear_data_files()
    gif_tags = ['see you next time']
    gif_url = json.loads(search_gif(query=gif_tags).text)['data'][0]['images']['fixed_height']['url']
    return render_template('goodbye.html', gif_url=gif_url, next_page="/index")
    # except: 
    #     return redirect('/error')


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

 


