import pickle
import re
from collections import deque
from textwrap import dedent

import tweepy

from .PostBot import PostBot


class TweetBot(PostBot):
    def __init__(
        self,
        name: str,
        credentials: dict[str, str],
        source_file: str,
        storage_threshold: int,
        chr_limit: int,
    ):
        self.storage_threshold = storage_threshold
        self.chr_limit = chr_limit
        super().__init__(name, credentials, source_file)

    def initClient(self):
        self.client = tweepy.Client(
            consumer_key=self.credentials["CONSUMER_KEY"],
            consumer_secret=self.credentials["CONSUMER_SECRET"],
            access_token=self.credentials["ACCESS_TOKEN"],
            access_token_secret=self.credentials["ACCESS_TOKEN_SECRET"],
        )

    def post(self):
        posts = self.getPosts()
        if self.validatePosts(posts):
            tweet = super().getRandomPost(posts)
            log_dict = self.__getRecentDict()
            try:
                self.initClient()
                self.client.create_tweet(text=tweet)
                log_dict[self.name].popleft()
                log_dict[self.name].append(tweet)
                with open("twt_recent.pkl", "wb") as f:
                    pickle.dump(log_dict, f)
            except tweepy.Forbidden as error:
                if "duplicate content" in str(error):
                    print(
                        f'[{self.name}] Error! Duplicate content found: "{tweet}". Try increasing your storage_threshold config value!'
                    )
                    print("Skipped:", self.name)
                else:
                    print(f"[{self.name}]", error)
                    print("Skipped:", self.name)
            except tweepy.TooManyRequests:
                print(
                    f"[{self.name}] Too many requests! Try running the script less often. (Free Tier of Twitter API: max 16.6 requests a day / 500 per month)"
                )
                print("Skipped:", self.name)
            except tweepy.TweepyException as error:
                print(f"[{self.name}]", error)
                print("Skipped:", self.name)
        else:
            print("Skipped:", self.name)

    def getPosts(self) -> list[str]:
        log = self.__getRecentDict()[self.name]
        try:
            with open(self.source_file, "r", encoding="utf-8") as f:
                return [
                    post.replace("\\n", "\n")
                    for post in re.findall(
                        r"^(?!#.*$)\S.*", f.read().strip("\n"), re.MULTILINE
                    )
                    if post not in log
                ]
        except FileNotFoundError:
            default_text = dedent(
                """
            # Place tweets here. There should be one tweet per line. If you have 'multi-line' tweets, write "\n" where you want your line breaks to be.
            # The script will ignore any empty lines, as well as lines that are 'commented' out with a "#".
            # It is up to you to ensure that each tweet is at maximum 280 characters long.
            # Please have at minimum 12 tweets in this file.
            # For the Free API of Twitter, also make sure you schedule it such that main.py does not run more often than every 90 minutes.
            """
            )
            with open(self.source_file, "w+") as f:
                f.write(default_text)
            print(
                f"Source file '{self.source_file}' not found. A clean file has been generated for you."
            )
            return []

    def __getRecentDict(self) -> dict[str, deque[str | None]]:
        try:
            with open("twt_recent.pkl", "rb") as f:
                log_dict = pickle.load(f)
        except FileNotFoundError:
            log_dict = {}
        if self.name not in log_dict:
            log_dict[self.name] = deque([None] * self.storage_threshold)
        return log_dict

    def validatePosts(self, posts: list[str]) -> bool:
        if not posts:
            print(
                f"Not enough posts in '{self.source_file}'! (Needed: {self.storage_threshold + 1} or more)"
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
