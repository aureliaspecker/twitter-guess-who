import json
from string import punctuation
import numpy as np
import os
import glob
from wordcloud import WordCloud, STOPWORDS
from matplotlib import pyplot as plt
import shortuuid
import pickle5 as pickle
import time
from .api_handler import Users_Lookup, Search_Counts, Recent_Search_Data, Statuses_Update


class TwitterGuessWho:
    """
    Controls Twitter guess who game.
    """


    def __init__(self, auth):
        """
        Initialise game parameters.
        """

        self.auth = auth
        self.users = []
        self.num_users = 0
        self.uuid = shortuuid.uuid()
        self.score = 0
        self.next_round = 1
        # Random seed so numbers change per game, but not between page reloads
        self.random_seed = np.random.randint(0,100)
        self.tweet_sent = False
        
        self.directory = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.join(self.directory, os.pardir)

    def add_user(self,user):
        """
        Add users based on Twitter handle
        :param user: str, Twitter handle 
        """

        # Add @ handle
        if user[0] != '@':
            user = f'@{user}'

        # Prevent duplicate entries
        error_code = 0
        if user in self.users:
            error_code = 1

        # Check if user exists and store
        if error_code == 0:
            user_lookup = Users_Lookup(self.auth)
            user_data = user_lookup(user[1:])
            user_exists = user_data.status_code == 200
            if user_exists:
                # Add official screen name in place of user input
                parsed = json.loads(user_data.text)
                screen_name = parsed[0]['screen_name']
                self.users.append(f'@{screen_name}')
                self.num_users += 1
                with open(f"{self.parent_dir}/data/user_data_{screen_name}_{self.uuid}.txt", "w") as user_file:
                    json.dump(user_data.text, user_file)
            else:
                error_code = 2

        return error_code


    def get_users(self):
        """
        Get all users.
        :return: list of str, users
        """

        return self.users


    def update_score(self, points):
        """
        Add points to current score.
        :param points: int
        """

        self.score += points


    def get_score(self):
        """
        Get current score
        :return: int, score
        """

        return self.score


    def get_shuffle(self, offset=0):
        """
        Get a shuffle of indices of same length as number of users.
        :return: list of int
        """

        np.random.seed(self.random_seed+offset)
        shuffle = np.arange(self.num_users)
        np.random.shuffle(shuffle)
        return shuffle


    def get_uniform_random_integer(self, lb=0, ub=40):
        """
        Get a random integer.
        :param lb: int, lower bound
        :param ub: int, upper bound
        :return: int, random uniformly generated in range
        """

        return np.random.randint(lb,ub)


    def clear_data_files(self):
        """
        Delete temporary data files from this game and old previous games.
        """

        # Delete tweet files
        data_files = glob.glob('./app/data/*{}*.txt'.format(self.uuid))
        for f in data_files:
            os.remove(f)

        # Delete wordcloud image files
        img_files = glob.glob('./app/static/img/wordcloud*{}*.png'.format(self.uuid))
        for f in img_files:
            os.remove(f)

        # Delete any previous old files from aborted games in last day
        time_threshold = time.time() - 24 * 60 * 60
        prev_data_files = glob.glob('./app/data/*.txt')
        prev_img_files = glob.glob('./app/static/img/wordcloud*.png')
        for f in prev_data_files:
            if os.stat(f).st_ctime < time_threshold:
                os.remove(f)
        for f in prev_img_files:
            if os.stat(f).st_ctime < time_threshold:
                os.remove(f)


    def make_api_calls(self):
        """
        Make API calls to get and store data ahead of the game. 
        """

        # Get Tweet counts for each user
        with open(f"{self.parent_dir}/data/tweet_counts_{self.uuid}.txt", "wb") as data_file:
            # Initiate empty dictionary
            counts_data = {} 
            # Get number of Tweets for each user
            search_counts = Search_Counts(self.auth)
            for i,user in enumerate(self.users):
                # Make API call
                response = search_counts(f"from:{user[1:]} -is:retweet")
                if response.status_code == 200:
                    response = response.text
                    parsed = json.loads(response)
                    counts_data[user] = parsed["totalCount"]
                else:
                    return False, response.status_code
            pickle.dump(counts_data, data_file)

        # Get recent Tweets for each user
        with open(f"{self.parent_dir}/data/recent_search_{self.uuid}.txt", "wb") as data_file:
            # Initiate empty dictionary
            tweet_data = {}
            # Get Tweets for each user
            recent_search_data = Recent_Search_Data(self.auth)
            for i,user in enumerate(self.users):
                # Make API call
                response = recent_search_data(f"from:{user[1:]} -is:retweet")
                if response.status_code == 200:
                    response = response.text
                    parsed = json.loads(response)
                    # Twitter Labs endpoint subject to change
                    try: 
                        tweet_data[user] = [tweet["text"] for tweet in parsed["data"]]
                    except: 
                        tweet_data[user] = None
                else:
                    return False, response.status_code
                    
            pickle.dump(tweet_data, data_file)

        # Store paths to wordcloud images
        self.wordcloud_paths = self.make_wordclouds()
        return True, 200


    def get_wordcloud_paths(self):
        """
        Get paths to image files for wordclouds.
        :return: list of str, wordcloud paths
        """

        return self.wordcloud_paths


    def get_tweet_counts(self,sort=True):
        """
        Get Tweet counts and corresponding users.
        :param sort: bool, sort tweet counts descending
        :return: list int, list str, of counts and users 
        """

        with open(f"{self.parent_dir}/data/tweet_counts_{self.uuid}.txt", "rb") as data_file:
            data = pickle.load(data_file)
            users = [k for k,v in data.items()]
            counts = [v for k,v in data.items()]
            if sort:
                users = np.array(users)
                counts = np.array(counts)
                sort_order = np.argsort(-counts)
                counts = [c for c in counts[sort_order]]
                users = [u for u in users[sort_order]]
        return counts, users


    def get_user_bio(self):
        """
        Get user bios from hydrated user object.
        :return: list of str, list of str, bios and corresponding users
        """

        users = []
        bios = []

        random_order = self.get_shuffle(1)
        for i in random_order:
            random_user = self.users[i]
            with open(f"{self.parent_dir}/data/user_data_{random_user[1:]}_{self.uuid}.txt", "rb") as user_file:
                data = json.load(user_file)
                parsed = json.loads(data)
                user = parsed[0]["screen_name"]
                bio = parsed[0]["description"]
                users.append(user)
                bios.append(bio)

        # Clean bios of stop words etc. and extract every 4 words only
        filtered_bios = self.clean_text(bios)
        for i,bio in enumerate(filtered_bios):
            filtered_bios[i] = " ".join(bio.split(" ")[::4]) # str->list->filter->str

        return filtered_bios, users


    def clean_text(self,text_items):
        """
        Convert text to lowercase, remove stop words and punctuation.
        :param text_items: list of str 
        :return: list of str
        """

        stop_words = set(STOPWORDS)
        stop_words.add('&amp')
        stop_words.add('amp')
        text_cleaned = []

        # Loop over text items
        for text in text_items:

            # Remove puntuation and make lowercase
            text_no_punc = text
            for p in punctuation:
                text_no_punc = text_no_punc.replace(p,"").lower()
            # Convert to list, remove common words and reform into string
            text_clean = [word for word in text_no_punc.split(" ") if word not in stop_words]
            text_cleaned.append(" ".join(text_clean))

        return text_cleaned


    def make_wordclouds(self):
        """
        Make wordclouds for each user from recent Tweets.
        :return: list of str, wordcloud paths
        """

        paths = []
        with open(f"{self.parent_dir}/data/recent_search_{self.uuid}.txt", "rb") as data_file:
            # Load tweets from file
            tweet_data = pickle.load(data_file)

            # Loop over users and make word cloud from tweets
            for user in self.users:

                # Get user Tweets
                tweets = tweet_data[user]

                # Make word cloud or use default image
                static_path = './app/static/'
                if tweets is not None:
                    # Clean tweets and combine into single string
                    cleaned_tweets = self.clean_text(tweets)
                    combined_tweets = " ".join(cleaned_tweets)
                    # Make wordcloud and save to static image directory
                    image_path = f'img/wordcloud_{user[1:]}_{self.uuid}.png'
                    path = f'{static_path}{image_path}'
                    twitter_wordcloud = WordCloud(width=480,height=480,margin=0,background_color="white",
                                              colormap="Blues",max_words=100).generate(combined_tweets)
                    plt.imshow(twitter_wordcloud, interpolation='bilinear')
                    plt.axis("off")
                    plt.margins(x=0, y=0)
                    plt.savefig(path,bbox_inches='tight',dpi=200)
                    plt.close()
                else:
                    image_path = 'img/larry_wordcloud.png'
                paths.append(image_path)

        return paths

    def post_status_update(self):
        """
        Post message to Twitter
        """
        if self.tweet_sent == False:
            statuses_update = Statuses_Update(self.auth)
            status = f"I just got a score of {self.score}/{self.num_users*3} playing Twitter Guess Who 🎉 \n \n Join me and play here: https://twitter-guess-who.herokuapp.com/"
            response = statuses_update(message=status)
            
            if response.status_code == 200: 
                self.tweet_sent = True
                return "Tweet sent!"
            else: 
                return "Something went wrong. We were unable to send your Tweet."
        else: 
            return "Tweet already sent!"