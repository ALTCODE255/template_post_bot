## Nameless' Post Bot Template

A template for making Twitter/Bluesky bots. Refactored from [template_twitter_bot](https://github.com/ALTCODE255/template_twitter_bot/).

### Requirements

1. Python 3.8+
2. For Twitter:
   1. A [Twitter App](https://developer.twitter.com/en/portal/) that uses Twitter API v2 and has "Read and write" user authentication app permissions
   2. At least 12 different possible tweets for the script to choose from. The more, the merrier.
3. For Bluesky:
   1. A Bluesky account and an [app password](https://bsky.app/settings/app-passwords).

### Instructions

1. [Download](https://github.com/ALTCODE255/template_post_bot/archive/refs/heads/master.zip) this Github repository and unzip it.

#### Configuration
2. Navigate to the `schemas` folder inside `configs`.
   - Delete or move `schema_bluesky.json` if you only plan on making bot(s) for Twitter.
   - Delete or move `schema_twitter.json` if you only plan on making bot(s) for Bluesky.
   - If you run bots for both, don't delete either file.
3. Go back to the `configs` folder. Open `twitter.json` (or `bluesky.json`) with your favorite text editor. Note: Do not rename this file.
4. Change the value of `name` to anything you want. This is how the script identifies the bot.
   - For Twitter: if you change this later on, you will lose the bot's recent tweets log stored in `twt_recent.pkl`. If you do this, delete the `twt_recent.pkl` file and let it regenerate itself on the script's next run.
5. Paste your API keys or app password into the `credentials` section.
   - For Twitter, OPTIONALLY:
     - Set `storage_threshold` to an integer higher than `11` for higher "randomness".
        - This variable indicates how many recent tweets the program stores (to avoid duplicate tweets).
     - Change `posts/tweetsFile.txt` to a different path or filename.
        - This variable indicates where you store your pool of potential tweets.
6. Change the value of `enabled` in the config file from `false` to `true`.
7. In the `.txt` file located in the `posts` folder (or other folder, if you changed it in step 3), fill the file with posts according to the guidelines specified.
    - For Twitter: If you changed `storage_threshold` in step 3, make sure the number of tweets you enter in this file is _higher_ than `storage_threshold`.

#### Running the Script
8. Use a task scheduler of your choice to schedule your machine to **run the Python file** however often you want your bot to post.
   - Ex. In crontab, you'd put `30 * * * * python path/to/template_post_bot/main.py` to have the script run every hour at the :30 minute mark.
   - For Twitter: Note that the rate limit for the Free Tier of API V2 is 500 posts per month, or 16 a day. Do not schedule for the script to run more often than this.
9.  (OPTIONAL) If you have multiple bots you want to run:
   1. Create a new `.txt` file for your new bot's source of post. Name it and place it whatever you like, but keep this filename and path in mind.
   2. Add a new section to the `.json` file in `configs` you modified earlier to set up your new bot in the same way you did in steps 3-7.
   3. Do this for however many bots you'd like to include.
10. That's it!

**NOTE FOR TWITTER:** Do _not_ delete the `recent.pkl` file from the folder unless you wish to reset the log of recent tweets. It is necessary for keeping a record of the most recently generated tweets to avoid being throttled by Twitter for duplicate tweets.
