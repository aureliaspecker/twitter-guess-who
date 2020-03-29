import os
from requests_oauthlib import OAuth1

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

    def generate_oauth1(self):
        return OAuth1(self.CONSUMER_KEY, self.CONSUMER_SECRET,
                   self.ACCESS_TOKEN, self.TOKEN_SECRET,
                   signature_method="HMAC-SHA1")

    def bearer_oauth(self, r):
        r.headers['Authorization'] = f"Bearer {self.BEARER_TOKEN}"
        r.headers['User-Agent'] = 'LabsResearchSearchQuickStartPython'
        return r
    
    def __str__(self):
        return f"Consumer key: {self.CONSUMER_KEY} \nConsumer secret: {self.CONSUMER_SECRET} \nAccess token: {self.ACCESS_TOKEN} \nToken secret: {self.TOKEN_SECRET} \nBearer token: {self.BEARER_TOKEN}"