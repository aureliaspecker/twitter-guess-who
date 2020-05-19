import os
from requests_oauthlib import OAuth1, OAuth1Session

class Authentication:
    """
    Class to handle Twitter credentials to access the API.
    """
    def __init__(self): 
        """
        Get access keys and tokens from os environment.
        """

        self.CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
        self.CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
        self.BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
        self.ENV = os.getenv("TWITTER_ENV")
        self.fetch_request_token()


    def generate_oauth1(self):
        """
        Generate OAuth1 using keys and secret.
        :return: OAuth1
        """

        return OAuth1(self.CONSUMER_KEY, self.CONSUMER_SECRET,
                   self.ACCESS_TOKEN, self.TOKEN_SECRET,
                   signature_method="HMAC-SHA1",signature_type='query')


    def generate_oauth1_session(self):
        """
        Generate OAuth1 using keys and secret.
        :return: OAuth1 session.
        """
        return OAuth1Session(client_key=self.CONSUMER_KEY, 
                            client_secret=self.CONSUMER_SECRET)
    
    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        :param r: 
        :return: 
        """
        r.headers['Authorization'] = f"Bearer {self.BEARER_TOKEN}"
        r.headers['User-Agent'] = 'LabsResearchSearchQuickStartPython'
        return r


    def __str__(self):
        """
        Write access formatted keys and tokens. 
        :return: str 
        """
        return f"Consumer key: {self.CONSUMER_KEY} \nConsumer secret: {self.CONSUMER_SECRET} \nAccess token: {self.ACCESS_TOKEN} \nToken secret: {self.TOKEN_SECRET} \nBearer token: {self.BEARER_TOKEN} \nRequset token: {self.oauth_token}"


    def fetch_request_token(self):
        """
        Fetches request token (step 1 of sign-in-with-twitter process)
        """
        auth = self.generate_oauth1_session() 
        url = "https://api.twitter.com/oauth/request_token"
        request_token_object = auth.get(url)
        oauth_data = self.str_to_dict(request_token_object.text)
        self.oauth_token = oauth_data['oauth_token']


    def get_sign_in_url(self):
        """
        Generates URL to redirect user to sign in with twitter
        """
        url = f"https://api.twitter.com/oauth/authorize?oauth_token={self.oauth_token}"
        return url


    def generate_user_tokens(self, path):
        """
        Generates user tokens from oauth_verifer retrieved at user redirect (step 3 of sign-in-with-twitter process)
        """

        oauth_data = self.str_to_dict(path)
        auth = self.generate_oauth1_session()
        url = "https://api.twitter.com/oauth/access_token"
        response = auth.post(url, data=oauth_data)
        user_tokens = self.str_to_dict(response.text)
        self.ACCESS_TOKEN = user_tokens['oauth_token']
        self.TOKEN_SECRET = user_tokens['oauth_token_secret']
        self.SCREEN_NAME = '@'+user_tokens['screen_name']


    def str_to_dict(self, input_string):
        """
        Convert string containing keys and values to dictionary.
        :param input_string: str, string of key/value pairs separated by = and &
        :return: dictionary of key/value 
        """

        # Remove question mark at start if present
        split_string = input_string
        if "?" in split_string:
            split_string = str.split(split_string,'?')[1]

        # Split on ampersands and extract keys and values by splitting on equals
        dict = {}
        split_string = str.split(split_string,'&')
        for kv_pair in split_string:
            k,v = str.split(kv_pair,'=')
            dict[k] = v

        return dict

