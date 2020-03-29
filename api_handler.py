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
        print(payload)
        return requests.request("POST", self.url, data=payload, headers=self.headers, auth=self.auth)


# class Recent_Search:
#     def __init__(self, url, max_results=100):
#         self.url = "https://api.twitter.com/labs/2/tweets/search"
#         self.max_results = max_results

#         self.headers = kwargs.get("headers", None)

#     def request(self, authentication):
#         self.response = requests.get(url=self.url, auth=authentication.BEARER_TOKEN, headers=self.headers)
