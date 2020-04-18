import console_text
from api_handler import Search_Counts, Recent_Search_Data
import numpy as np
import json

class RoundBase:
    """
    Base class for rounds in Twitter guess-who.
    Each derived round class must have the following methods:
    1) header()
    2) generate_answers()
    """

    number = 0

    def __init__(self):

        print("You shouldn't be instantiating this class!!")


    def __call__(self, auth, users):
        """
        :param auth: authentication
        :param users: list of users
        :return: 
        """

        self.auth = auth
        self.users = np.array(users)
        self.num_users = self.users.size

        # Write header
        self.header()

        # Generate round answers
        self.generate_answers()

        # Play round
        self.play()


    def play(self):
        """
        Display users and possible answers.
        Get player guesses and compare to answers to calculate score.
        """

        # Initialisation
        attempts = 0 # Total number of attempts
        user_answers = {}
        for i,user in enumerate(self.users):
            user_answers[user] = self.answers[i]


        # Player can have as many attempts at matching answers as they like, but each attempt costs points
        while True:

            # Get remaining users and answers
            users = []
            answers = []
            for u,a in user_answers.items():
                users.append(u)
                answers.append(a)
            users = np.array(users)
            answers = -np.sort(-np.array(answers)) ### ANSWERS MUST BE INT/FLOAT - REVISIT IF USING STRINGS

            # Display users and answers
            console_text.write_message('Users:')
            console_text.write_options_letter(users)
            console_text.write_message('Options:')
            console_text.write_options_numeric(answers)

            # Get player guesses
            player_guesses = {}
            console_text.write_message('OK, so which number corresponds to:\n')
            for i, user in enumerate(users):
                player_guesses[user] = answers[console_text.integer_question(user, lower_bound=1, upper_bound=users.size) - 1]

            # Compare player guesses against user answers
            correct_users = []
            for user,guess in player_guesses.items():
                answer = user_answers[user]
                if guess==answer:
                    correct_users.append(user)

            # Update score and remove correct users
            self.score += len(correct_users)
            for user in correct_users:
                user_answers.pop(user)

            # Check if player wants to play again or stop
            console_text.write_message(('You just got {} points. The following users are correct: '+'{} '*len(correct_users)).format(len(correct_users),*correct_users))
            if len(user_answers)==0:
                break
            reattempt = console_text.yes_no_question('\nWould you like to retry for 1 point?')
            if reattempt:
                self.score -= 1
            else:
                break

        console_text.write_message('\nYour current score is...')
        console_text.write_message('{} points!'.format(self.score))


class RoundTweetCount(RoundBase):
    """
    Round where players guess users based on their recent tweet counts.
    """


    def __init__(self,**kwargs):
        """
        
        """

        self.score = 0


    def header(self):
        """
        Write round header.
        """

        self.number += 1
        console_text.write_round(self.number)
        console_text.write_message("This is the tweet count round!\nYou must match the number of tweets to each user.\nOne point for each correct answer!\n")


    def generate_answers(self):
        """
        Get number of Tweets for each user.
        :return: 
        """

        # Get number of Tweets for each user
        tweet_counts = np.zeros(self.num_users, dtype=int)
        search_counts = Search_Counts(self.auth)
        for i, user in enumerate(self.users):
            response = search_counts(f"from:{user[1:]} -is:retweet")
            parsed = json.loads(response.text)
            tweet_counts[i] = parsed['totalCount']

        # Store number of Tweets as answers
        self.answers = tweet_counts

