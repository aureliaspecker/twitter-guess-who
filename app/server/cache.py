import datetime as dt
import json
import glob
import os
import re


def cache_response(user,response,keyword):
    """
    Cache user response, dumping json to file with keyword, date and time stamp.
    Delete any previous cache from same user and keyword.
    :param user: str, user name
    :param response: json, response
    :param keyword: str, cache identifier
    :return: 
    """

    # Delete previous caches
    previous_caches = glob.glob(f'./user_cache/{user[1:]}_{keyword}*.txt')
    for file in previous_caches:
        os.remove(file)

    # Generate new cache
    cache_datetime = dt.datetime.utcnow().strftime("%Y%m%d%H%M")
    cache_file = f'./user_cache/{user[1:]}_{keyword}_{cache_datetime}.txt'
    with open(cache_file,'w') as f:
        json.dump(response,f)


def load_cache(user,keyword,time_frame):
    """
    Load cached user response within given time frame.
    :param user: str, user name
    :param keyword: str, cache identifier
    :param time_frame: int, hours
    :return: response or None
    """

    # Check for previous cache
    cache = glob.glob(f'./user_cache/{user[1:]}_{keyword}*.txt')
    if len(cache)==0:
        return None

    # Check previous cache within time frame
    cache = cache[0]
    cache_datetime = re.search(f'./user_cache/{user[1:]}_{keyword}_(.+?).txt', cache).group(1)
    cache_datetime = dt.datetime.strptime(cache_datetime,'%Y%m%d%H%M')
    now = dt.datetime.utcnow()
    time_diff = (now-cache_datetime)/dt.timedelta(hours=1)
    if time_diff>time_frame:
        return None

    # Load cache if within time frame
    with open(cache,'r') as f:
        response = json.load(f)

    return response

