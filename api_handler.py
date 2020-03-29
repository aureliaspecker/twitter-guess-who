import os
import requests

class Search_Counts: 
    def __init__(self, authentication, bucket="day"):
        self.env = os.getenv("ENV")
        if self.env == None: 
            raise ValueError("Environment variable not found")
        self.url = f"https://api.twitter.com/1.1/tweets/search/30day/{self.env}/counts.json" 
        self.headers = {
            "content-type": "application/json"
        }
        self.auth = authentication.generate_oauth1()
        self.bucket = bucket
        

    def __call__(self, query):
        payload = "{{\n\t\"query\": \"{}\", \n\t\"bucket\": \"{}\"\n}}".format(query, self.bucket)
        return requests.request("POST", self.url, data=payload, headers=self.headers, auth=self.auth)

class Recent_Search_Data: 
    def __init__(self, authentication, max_results=100):
        self.url = "https://api.twitter.com/labs/2/tweets/search"
        self.max_results = max_results
        self.auth = authentication.bearer_oauth
        self.headers = {
            "Accept-Encoding": "gzip"
        }
        print(self.headers)
        self.payload = ""

    def __call__(self, query):
        querystring = {"query": query,"max_results":"100"} 
        return requests.request("GET", url=self.url, data=self.payload, auth=self.auth, headers=self.headers, params=querystring)