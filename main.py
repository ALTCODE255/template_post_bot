import os
import sys
import glob

from src.BskyBot import BskyBot
from src.TweetBot import TweetBot
from src.configs import loadConfig

if __name__ == "__main__":
    os.chdir(sys.path[0])

    for schema_file in glob.glob("configs/schemas/schema_*.json"):
        config_file = schema_file.replace("configs/schemas/schema_", "configs/")
        conf_list = loadConfig(config_file, schema_file)
        for bot_conf in conf_list:
            match (schema_file):
                case "bluesky":
                    if bot_conf["enabled"]:
                        bot_client = BskyBot(
                            bot_conf["name"],
                            bot_conf["credentials"],
                            bot_conf["filepath"],
                        )
                        bot_client.post()
                case "twitter":
                    if bot_conf["enabled"]:
                        bot_client = TweetBot(
                            bot_conf["name"],
                            bot_conf["credentials"],
                            bot_conf["filepath"],
                            bot_conf["storage_threshold"],
                            bot_conf["chr_limit"],
                        )
                        bot_client.post()
