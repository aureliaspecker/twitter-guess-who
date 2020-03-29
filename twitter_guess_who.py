import glob
import json
import console_text
from authentication import Authentication
from api_handler import Search_Counts, Recent_Search_Data
from string import punctuation
import numpy as np
np.random.seed(0)

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

        # Game containers
        self.users = []


    def __call__(self):
        """
        Run Twitter Guess Who game.
        """

        self.welcome()
        self.setup()
        self.round_tweet_counts()
        self.round_word_cloud()


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
        if predefined:
            successful_load = self.load_predefined_user_set()
        else:
            successful_load = False
        if successful_load:
            self.num_users = len(self.users)
            console_text.write_message("User set loaded successfully!")
            console_text.write_list("Users are:",self.users)
        else:
            raise ValueError("Not yet implemented!!!")
        console_text.write_message("OK we are ready to play!")


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
        :param handle: str, Twitter handle 
        """

        self.users.append(f'@{user}')


    def round_tweet_counts(self):
        """
        Game round - Guess users from number of tweets.
        """

        # Get number of tweets for each user
        tweet_count = []
        search_counts = Search_Counts(self.auth)
        for user in self.users:
            response = search_counts(f"from:{user[1:]} -is:retweet")
            parsed = json.loads(response.text)
            tweet_count.append(parsed['totalCount'])

        # 
        random_order = np.arange(self.num_users,dtype=int)
        np.random.shuffle(random_order)

    def round_word_cloud(self):
        """
        Game round - Guess from wordcloud.
        """

        # Get data
        recent_search_data = Recent_Search_Data(self.auth)
        for user in self.users: 
            response = recent_search_data(f"from:{user[1:]} -is:retweet")
            parsed = json.loads(response.text)
            tweet_text = [tweet["text"] for tweet in parsed["data"]]

        # Remove punctuation, make lowercase, store separate words in a list
        word_list = []
        for text in tweet_text:
            for p in punctuation: 
                text = text.replace(p, "").lower()
                for word in text.split(" "):
                    word_list.append(word)

        # ToDo --> separate above data per user. Then, generate wordcloud for each user.