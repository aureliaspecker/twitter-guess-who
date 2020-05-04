import requests
import datetime as dt


class Users_Lookup:
    """
    Get fully hydrated user obejects.
    """

    def __init__(self, authentication):
        """
        :param authentication: Authentication object (see authentication.py)
        """

        self.url = f"https://api.twitter.com/1.1/users/lookup.json"
        self.auth = authentication.generate_oauth1()


    def __call__(self, query):
        """
        :param query: str
        :return: user objects for specified query
        """

        url = f'{self.url}?screen_name={query}'
        return requests.request("GET", url=url, auth=self.auth)

class Search_Counts:
    """
    Full archive search counts endpoint.
    """

    def __init__(self, authentication, bucket="day"):
        """
        :param authentication: Authentication object (see authentication.py)
        :param bucket: unit of time for which counts data is provided
        """

        env = authentication.ENV
        if env == None:
            raise ValueError("Environment variable not found")
        self.url = f"https://api.twitter.com/1.1/tweets/search/fullarchive/{env}/counts.json"
        self.headers = {
            "content-type": "application/json"
        }
        self.auth = authentication.generate_oauth1()
        self.bucket = bucket
        self.to_date = (dt.datetime.utcnow() + dt.timedelta(minutes=-1)).strftime("%Y%m%d%H%M")
        self.from_date = (dt.datetime.utcnow() + dt.timedelta(days=-28,minutes=-1)).strftime("%Y%m%d%H%M")


    def __call__(self, query):
        """
        :param query: str
        :return: data volumes for specified query
        """

        payload = "{{\n\t\"query\": \"{}\", \n\t\"bucket\": \"{}\",\n\t\t\"fromDate\": \"{}\",\n\t\t\"toDate\": \"{}\"\n}}".format(query, self.bucket, self.from_date, self.to_date)
        return requests.request("POST", self.url, data=payload, headers=self.headers, auth=self.auth)


class Recent_Search_Data:
    """
    Recent search endpoint, Twitter Developer Labs.
    """

    def __init__(self, authentication, max_results=100):
        """
        :param authentication: Authentication object (see authentication.py)
        :param max_results: max number of search results per request
        """

        self.url = "https://api.twitter.com/labs/2/tweets/search"
        self.max_results = max_results
        self.auth = authentication.bearer_oauth
        self.headers = {
            "Accept-Encoding": "gzip"
        }
        self.payload = ""


    def __call__(self, query):
        """
        :param query: str
        :return: tweet payload for results matching query in previous 7 days
        """

        querystring = {"query": query,"max_results":"100"} 
        return requests.request("GET", url=self.url, data=self.payload, auth=self.auth, headers=self.headers, params=querystring)


class Followers_Ids:
    """
    Followers ids endpoint.
    """

    def __init__(self, authentication):
        """
        :param authentication: Authentication object (see authentication.py)
        """

        self.url = "https://api.twitter.com/1.1/followers/ids.json"
        self.headers = {
            "content-type": "application/json"
        }
        self.auth = authentication.generate_oauth1()


    def __call__(self, query):
        """
        :param query: str, user 
        :return: user ids corresponding to followers of given user
        """

        querystring = "{{\"screen_name\": \"{}\"}}".format(query)
        requests.get(self.url, params=querystring, auth=self.auth)
        return requests.get(self.url, params=querystring, auth=self.auth)


class Random_Gif:
    """
    GIPHY API random gif endpoint.    
    """

    def __init__(self, authentication_key):
        """
        :param authentication_key: str, api key
        """

        self.url = f"https://api.giphy.com/v1/gifs/random?api_key={authentication_key}"


    def __call__(self, tags, limit=1):
        """
        :param tags: str, or list of string
        :return: single gif object
        """

        if isinstance(tags,str):
            url = self.url + "&tag=" + tags + f"&limit={limit}"
        elif isinstance(tags,list):
            url = self.url + "&tag=" + '+'.join(tags) + f"&limit={limit}"
        return requests.get(url=url)


class Search_Gif:
    """
    GIPHY API search gif endpoint.
    """


    def __init__(self, authentication_key):
        """
        :param authentication_key: str, api key
        """

        self.url = f"https://api.giphy.com/v1/gifs/search?api_key={authentication_key}"


    def __call__(self, query, limit=10, rating='g', lang='en'):
        """
        :param query: gif tags
        :param limit: number of gifs
        :param rating: content suitability rating
        :param lang: language
        :return: json response containing list of gifs 
        """

        url = f'{self.url}&q={query}&limit={limit}&rating={rating}&lang={lang}'
        return requests.get(url=url)
