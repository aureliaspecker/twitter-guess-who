import glob
import console_text

class TwitterGuessWho:
    """
    Controls Twitter guess who game.
    """


    def __init__(self,**kwargs):
        """
        Initialise game parameters.
        """

        self.users = []


    def __call__(self):
        """
        Run Twitter Guess Who game.
        """

        self.welcome()
        self.setup()


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
            console_text.write_message("User set loaded successfully!")
            console_text.write_list("Users are:",self.users)
        else:
            raise ValueError("Not yet implemented!!!")



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



    def add_user(self,user):
        """
        Add users based on Twitter handle or user ID
        :param handle: str, Twitter handle 
        """

        self.users.append(f'@{user}')