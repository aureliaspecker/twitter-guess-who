# Twitter Guess Who

## Authentication
Authentication is handled in `app/server/authentication.py` 

You will need a Twitter [developer account](https://developer.twitter.com/en/account/get-started) ([apply here](https://developer.twitter.com/en/apply-for-access) if you don't already have one).

You will also need to create a new app with [GIPHY for Developers](https://developers.giphy.com/dashboard/).

The application looks for your keys and credentials in your os environment. You must therefore export your keys like so: 

```
export TWITTER_CONSUMER_KEY=XXXXXXXXXXXXXXXXX
export TWITTER_CONSUMER_SECRET=XXXXXXXXXXXXXX
export TWITTER_BEARER_TOKEN=XXXXXXXXXXXXXXXXX
export TWITTER_ENV=xxx 
export GIPHY_KEY=XXXXXXXXXXXXXXXXX
```

You can find your Twitter consumer key and Twitter consumer secret in your Twitter developer portal, under [app details](https://developer.twitter.com/en/apps/).

You can use [this tool](https://glitch.com/~twitter-bearer-token) to generate a Twitter bearer token.

You can find your Twitter environment variable in your twitter developer portal under [Dev environments](https://developer.twitter.com/en/account/environments).

You can find your GIPHY API key on your GIPHY [developer dashboard](https://developers.giphy.com/dashboard/).

Note: The Twitter access token and access token secret required with some of the Twitter APIs is generated with [Sign In With Twitter](https://developer.twitter.com/en/docs/basics/authentication/guides/log-in-with-twitter) when a user first starts playing the game.