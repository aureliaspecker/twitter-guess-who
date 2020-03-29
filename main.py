from twitter_guess_who import TwitterGuessWho

def main():

    tgw = TwitterGuessWho()
    tgw()

    # search_counts = Search_Counts(auth)
    # response_search_counts = search_counts("from:AureliaSpecker -is:retweet")
    # print(response_search_counts.text)
    #
    # recent_search_data = Recent_Search_Data(auth)
    # response_recent_search_data = recent_search_data("from:AureliaSpecker -is:retweet")
    # print(response_recent_search_data.text)

if __name__ == "__main__":
    main()
