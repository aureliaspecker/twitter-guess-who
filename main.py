from authentication import Authentication
from api_handler import Search_Counts, Recent_Search_Data

def main():
    auth = Authentication()
    print(auth)

    search_counts = Search_Counts(auth)
    response_search_counts = search_counts("from:AureliaSpecker -is:retweet")
    print(response_search_counts.text)

    recent_search_data = Recent_Search_Data(auth)
    response_recent_search_data = recent_search_data("from:AureliaSpecker -is:retweet")
    print(response_recent_search_data.text)

if __name__ == "__main__":
    main()