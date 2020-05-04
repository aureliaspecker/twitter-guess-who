import glob
import json
import time
from .console_text import *
from .rounds import *
from .authentication import Authentication
from .api_handler import Users_Lookup, Search_Counts, Recent_Search_Data
from string import punctuation
import numpy as np
from nltk.corpus import stopwords
from wordcloud import WordCloud
from matplotlib import pyplot as plt
import shortuuid
import pickle5 as pickle

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


    def __call__(self):
        """
        Run Twitter Guess Who game.
        """

        self.welcome()
        self.setup()
        round1 = rounds.RoundTweetCount()
        round1(self.auth,self.users)
        # round2 = rounds.RoundFollowerCount()
        # round2(self.auth, self.users)


    def welcome(self):
        """"
        Write welcome message to screen.
        """

        console_text.write_welcome()


    def setup(self):
        """
        Get game setup from command line options.
        """

        # Get user set
        console_text.write_message("Let's start by setting up your game!\nFirst let's get the users.")
        predefined = console_text.yes_no_question("Would you like to use a predefined user set?")
        self.users = []
        if predefined:
            successful_load = self.load_predefined_user_set()
        else:
            successful_load = False
        if successful_load:
            self.users = np.array(self.users)
            self.num_users = self.users.size
            console_text.write_message("User set loaded successfully!")
            console_text.write_list("Users are:",self.users)
        else:
            raise ValueError("Not yet implemented!!!")
        console_text.write_message("OK we are ready to play!")
        console_text.write_dashes()
        time.sleep(1)

        # Setup scoring
        self.score = 0


    def load_predefined_user_set(self):
        """
        Load set of predefined users based on Twitter handles or user IDs.
        Located in ./user_sets/*.txt 
        :return: bool, whether load is successful
        """

        # Find predefined sets
        set_options = glob.glob('./user_sets/*.txt')

        # If no sets abort
        if len(set_options)==0:
            console_text("Sorry no predefined user sets have been added yet")
            return False

        # Load chosen set
        option = console_text.option_question("Which user set would you like?",set_options)
        with open(set_options[option],'r') as f:
            for line in f:
                self.add_user(line.split()[0])
        return True


    def command_line_user_set(self):
        """
        Get set of users (Twitter handles/user IDs) from command line.
        """
        pass


    def add_user(self,user):
        """
        Add users based on Twitter handle or user ID
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
        self.score += points

    def get_score(self):
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


    def round_tweet_counts(self):
        """
        Game round - Guess users from number of tweets.
        """

        # Header
        self.round_count += 1
        console_text.write_round(self.round_count)
        console_text.write_message("This is the tweet count round!\nYou must match the number of tweets to each user.\nOne point for each correct answer!\n")

        # Get number of tweets for each user
        tweet_counts = np.zeros(self.num_users,dtype=int)
        search_counts = Search_Counts(self.auth)
        for i,user in enumerate(self.users):
            response = search_counts(f"from:{user[1:]} -is:retweet")
            parsed = json.loads(response.text)
            tweet_counts[i] = parsed['totalCount']

        # Display options
        console_text.write_message('Users:')
        console_text.write_options_letter(self.users)
        sort_order = np.argsort(-tweet_counts)
        sorted_tweet_counts = tweet_counts[sort_order]
        console_text.write_message('Tweet counts:')
        console_text.write_options_numeric(sorted_tweet_counts)

        # Get guesses and compare to answers
        attempts = 0 # number of attempts
        compare_answers = np.zeros(self.num_users,dtype=bool) # Boolean whether player answer matches correct answer
        while True:
            guesses = np.zeros_like(self.users,dtype=int)
            console_text.write_message('OK, so which number corresponds to:\n')
            for i,user in enumerate(self.users):
                if compare_answers[i]==0: # Ask question only if not correct last time
                    guesses[i] = console_text.integer_question(user,lower_bound=1,upper_bound=self.num_users)-1
            attempts += 1
            compare_answers = [sort_order[i]==guesses[i] for i in range(self.num_users)]
            correct_answers = np.sum(compare_answers)
            if correct_answers==self.num_users and attempts==1:
                console_text.write_message('You got them all correct first time! Amazing!')
                break
            elif correct_answers==self.num_users:
                console_text.write_message('You got them all correct now, nice!')
                break
            else:
                console_text.write_message(('You got {} correct: '+'{} '*correct_answers).format(correct_answers,*self.users[compare_answers]))
                reattempt = console_text.yes_no_question('Would you like to retry for 1 point?')
                if not reattempt:
                    break
        self.score += correct_answers-(attempts-1)
        print(self.score)
        console_text.write_dashes()
        

    def make_user_wordclouds(self):
        """
        
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
                path = f'./app/static/img/wordcloud_{user}_{self.uuid}.png'
                twitter_wordcloud = WordCloud(width=480,height=480,margin=0,
                                              colormap="coolwarm",max_words=100).generate(combined_tweets)
                plt.imshow(twitter_wordcloud, interpolation='bilinear')
                plt.axis("off")
                plt.margins(x=0, y=0)
                plt.savefig(path,bbox_inches=None)
                plt.close()
                paths.append(path)

        return paths

