
class TwitterGuessWho:
    """
    Controls Twitter guess who game.
    """


    def __init__(self,**kwargs):
        """
        Initialise game parameters.
        """

        # Load users for game
        user_set = kwargs.get('user_set',None)
        self.users = []
        if user_set is not None:
            self.load_user_set(user_set)


    def load_user_set(self,user_set):
        """
        Load set of predefined users based on Twitter handles or user IDs.
        :param user_set: str, name of file containing handles in ./user_sets/*.txt 
        """

        try:
            with open(f'./user_sets/{user_set}.txt','r') as f:
                for line in f:
                    self.add_user(line.split()[0])
        except:
            print('Could not load user set: {0}\nFile ./user_sets/{0}.txt not found'.format(user_set))


    def add_user(self,user):
        """
        Add users based on Twitter handle or user ID
        :param handle: str, Twitter handle 
        """

        self.users.append(user)