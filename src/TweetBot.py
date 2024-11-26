from contextlib import closing
import re
import sqlite3

import tweepy

from .PostBot import PostBot


class TweetBot(PostBot):

    def __init__(
        self,
        name: str,
        credentials: dict[str, str],
        source_file: str,
        log_thres: int,
        chr_limit: int,
    ):
        self.log_thres = log_thres
        self.chr_limit = chr_limit
        super().__init__(name, credentials, source_file, log_thres)

    @property
    def SCHEMA_NAME(self) -> str:
        return "Twitter"

    @property
    def DEFAULT_FILE_TEXT(self) -> str:
        return """
            # Place tweets here. There should be one tweet per line. If you have 'multi-line' tweets, write "\n" where you want your line breaks to be.
            # The script will ignore any empty lines, as well as lines that are 'commented' out with a "#".
            # It is up to you to ensure that each tweet is at maximum 280 characters long.
            # Please have at minimum 12 tweets in this file.
            # For the Free API of Twitter, also make sure you schedule it such that main.py does not run more often than every 90 minutes.
            """

    def initClient(self):
        self.client = tweepy.Client(
            consumer_key=self.credentials["CONSUMER_KEY"],
            consumer_secret=self.credentials["CONSUMER_SECRET"],
            access_token=self.credentials["ACCESS_TOKEN"],
            access_token_secret=self.credentials["ACCESS_TOKEN_SECRET"],
        )

    def validatePosts(self, posts: list[str]) -> bool:
        if not posts:
            print(
                f"Not enough posts in '{self.source_file}'! (Needed: {self.log_thres + 1} or more)"
            )
            return False
        exceeding_tweets = [tweet for tweet in posts if len(tweet) > self.chr_limit]
        if exceeding_tweets:
            print(
                f"One or more tweets in '{self.source_file}' exceeds the character limit set ({self.chr_limit}):\n- "
                + "\n- ".join(exceeding_tweets)
            )
            return False
        return True

    def _postLogic(self, post) -> bool:
        try:
            self.initClient()
            self.client.create_tweet(text=post)
            return True
        except tweepy.Forbidden as error:
            if "duplicate content" in str(error):
                print(
                    f'[{self.name}] Error! Duplicate content found: "{post}". Try increasing your log_thres config value!'
                )
            else:
                print(f"[{self.name}]", error)
            return False
        except tweepy.TooManyRequests:
            print(
                f"[{self.name}] Too many requests! Try running the script less often. (Free Tier of Twitter API: max 16.6 requests a day / 500 per month)"
            )
            return False
        except tweepy.TweepyException as error:
            print(f"[{self.name}]", error)
            return False
