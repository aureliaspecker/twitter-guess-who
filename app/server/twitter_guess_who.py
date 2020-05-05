import glob
import json
import time
from string import punctuation
import numpy as np
from nltk.corpus import stopwords
from wordcloud import WordCloud
from matplotlib import pyplot as plt
import shortuuid
import pickle5 as pickle
from .authentication import Authentication
from .api_handler import Users_Lookup, Search_Counts, Recent_Search_Data

class TwitterGuessWho:
    """
    Controls Twitter guess who game.
    """


    def __init__(self,**kwargs):
        """
        Initialise game parameters.
        """

        # Authentication
        self.auth = Authentication()
        self.users = []
        self.num_users = 0
        self.uuid = shortuuid.uuid()
        self.score = 0
        self.next_round = 1


    def add_user(self,user):
        """
        Add users based on Twitter handle
        :param user: str, Twitter handle 
        """

        # Add @ handle
        if user[0] != '@':
            user = f'@{user}'

        # Check if user exists and store
        user_lookup = Users_Lookup(self.auth)
        user_data = user_lookup(user[1:])
        user_exists = user_data.status_code == 200
        if user_exists:
            # Add official screen name in place of user input
            parsed = json.loads(user_data.text)
            screen_name = parsed[0]['screen_name']
            self.users.append(f'@{screen_name}')
            self.num_users += 1
            with open(f"./app/data/user_data_{user[1:]}_{self.uuid}.txt", "w") as user_file:
                json.dump(user_data.text, user_file)

        return user_exists


    def get_users(self):
        """
        Get all users.
        :return: list of str
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


    def make_api_calls(self):
        """
        Make API calls to get and store data ahead of the game. 
        :return: 
        """

        # Get Tweet counts for each user
        with open(f"./app/data/tweet_counts_{self.uuid}.txt", "wb") as data_file:
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
                    raise ValueError("Unsuccessful API call")
            pickle.dump(counts_data, data_file)

        # Get recent Tweets for each user
        with open(f"./app/data/recent_search_{self.uuid}.txt", "wb") as data_file:
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
                    tweet_data[user] = [tweet["text"] for tweet in parsed["data"]]
                else:
                    raise ValueError("Unsuccessful API call")
            pickle.dump(tweet_data, data_file)
        # Store paths to wordcloud images
        self.wordcloud_paths = self.make_wordclouds()


    def get_wordcloud_paths(self):
        """
        Get paths to image files for wordclouds.
        :return: 
        """
        return self.wordcloud_paths


    def get_tweet_counts(self,sort=True):
        """
        Get Tweet counts and corresponding users.
        :param sort: bool, sort tweet counts descending
        :return: list int, list str, of counts and users 
        """

        with open(f"./app/data/tweet_counts_{self.uuid}.txt", "rb") as data_file:
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


    def get_user_bio(self,seed=0):
        """
        Get user bios from hydrated user object.
        """
        users = []
        bios = []

        np.random.seed(seed)
        random_order = np.arange(self.num_users)
        np.random.shuffle(random_order)
        for i in random_order:
            random_user = self.users[i]
            with open(f"./app/data/user_data_{random_user[1:]}_{self.uuid}.txt", "rb") as user_file:
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

        stop_words = set(stopwords.words('english'))
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
        """

        paths = []
        with open(f"./app/data/recent_search_{self.uuid}.txt", "rb") as data_file:
            # Load tweets from file
            tweet_data = pickle.load(data_file)

            # Loop over users and make word cloud from tweets
            for user in self.users:
                # Clean up tweets and combine
                tweets = tweet_data[user]
                cleaned_tweets = self.clean_text(tweets)
                combined_tweets = " ".join(cleaned_tweets)

                # Make word cloud
                base = './app/static/'
                image = f'img/wordcloud_{user[1:]}_{self.uuid}.png'
                path = f'{base}{image}'
                twitter_wordcloud = WordCloud(width=480,height=480,margin=0,
                                              colormap="coolwarm",max_words=100).generate(combined_tweets)
                plt.imshow(twitter_wordcloud, interpolation='bilinear')
                plt.axis("off")
                plt.margins(x=0, y=0)
                plt.savefig(path,bbox_inches=None)
                plt.close()
                paths.append(image)

        return paths

