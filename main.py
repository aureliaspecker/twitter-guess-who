from authentication import Authentication
from api_handler import Search_Counts

def main():
    auth = Authentication()
    print(auth)

    search_counts = Search_Counts(auth)
    response = search_counts("from:AureliaSpecker")
    print(response.text)

if __name__ == "__main__":
    main()