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
        user_exists = user_lookup(user[1:]).status_code == 200
        if user_exists:
            self.users.append(f'{user}')
            self.num_users += 1

        return user_exists

    def get_user_data(self):
        """
        Make API calls to get and store data ahead of the game. 
        :return: 
        """

        #Get Tweet counts for each user
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
                    # Save data to text file
                else: 
                    raise ValueError("Unsuccessful API call")
            pickle.dump(counts_data, data_file)

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
        

    def round_word_cloud(self):
        """
        Game round - Guess from wordcloud.
        """

        # Header
        self.round_count += 1
        console_text.write_round(self.round_count)
        console_text.write_message("This is the word cloud round!\nYou must match the word cloud to each user.\nOne point for each correct answer!\n")

        recent_search_data = Recent_Search_Data(self.auth)
        stop_words = set(stopwords.words('english'))

        for user in self.users:
            
            #Gets data for each user
            response = recent_search_data(f"from:{user[1:]} -is:retweet")
            parsed = json.loads(response.text)
            tweet_text = [tweet["text"] for tweet in parsed["data"]]
            
            all_words = []

            for text in tweet_text:

                #Removes punctuation & makes lowercase
                for p in punctuation: 
                    text = text.replace(p, "").lower()
                
                #Stores all the words in a list
                for word in text.split(" "):
                    all_words.append(word)

            # Remove common words
            filtered_words_list = [word for word in all_words if not word in stop_words]
            filtered_words = " ".join(filtered_words_list)
            print(filtered_words)

        # Generate wordcloud for each user
        twitter_wordcloud = WordCloud(
            width=480, 
            height=480, 
            margin=0, 
            colormap="coolwarm", 
            max_words=100
        ).generate(filtered_words)

        # Display the generated image:
        plt.imshow(twitter_wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.margins(x=0, y=0)
        plt.show()

        # ToDo --> Scores 

        console_text.write_dashes()
