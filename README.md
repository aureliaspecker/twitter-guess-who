# Twitter Guess Who

## Authentication
You must export your Twitter keys and access tokens, like so: 

```
export TWITTER_CONSUMER_KEY=XXXXXXXXXXXXXXXXX
export TWITTER_CONSUMER_SECRET=XXXXXXXXXXXXXX
export TWITTER_ACCESS_TOKEN=XXXXXXXXXXXXXXXXX
export TWITTER_ACCESS_TOKEN_SECRET=XXXXXXXXXX
export TWITTER_BEARER_TOKEN=XXXXXXXXXXXXXXXXX
```

You can find your consumer key, consumer secret, access token, and access token secret in your Twitter developer portal, under app details: https://developer.twitter.com/en/apps/

You can use this tool to generate a bearer token: https://glitch.com/~twitter-bearer-token 

## Environment variables
In order to get counts data, you must also export your dev environment for the Premium Search API. You can find this in your developer portal, under dev environments: https://developer.twitter.com/en/account/environments

For example: 
```
export ENV=prod 
```