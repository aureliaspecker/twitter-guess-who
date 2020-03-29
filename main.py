from authentication import Authentication
from twitter_guess_who import TwitterGuessWho

def main():

    auth = Authentication()
    tgw = TwitterGuessWho()
    tgw()

if __name__ == "__main__":
    main()