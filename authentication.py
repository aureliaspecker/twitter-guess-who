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
        self.ENV = os.getenv("TWITTER_ENV")


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
        return f"Consumer key: {self.CONSUMER_KEY} \nConsumer secret: {self.CONSUMER_SECRET} \nAccess token: {self.ACCESS_TOKEN} \nToken secret: {self.TOKEN_SECRET} \nBearer token: {self.BEARER_TOKEN}"