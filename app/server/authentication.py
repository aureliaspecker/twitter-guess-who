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
        self.ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
        self.TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
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
        auth = OAuth1Session(client_key=self.CONSUMER_KEY, client_secret=self.CONSUMER_SECRET) 
        url = "https://api.twitter.com/oauth/request_token"
        request_token_object = (auth.get(url))
        request_token_text = str.split(request_token_object.text, '&') 
        self.oauth_token = str.split(request_token_text[0], '=')[1]
    
    def get_sign_in_url(self):
        """
        Generates URL to redirect user to sign in with twitter
        """
        url = f"https://api.twitter.com/oauth/authorize?oauth_token={self.oauth_token}"
        return url