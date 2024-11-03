import os
import sys
import glob

from src.BskyBot import BskyBot
from src.TweetBot import TweetBot
from src.configs import loadConfig

if __name__ == "__main__":
    os.chdir(sys.path[0])

    for schema_file in map(
        os.path.basename, glob.glob("configs/schemas/schema_*.json")
    ):
        config_file = schema_file.strip("schema_")
        conf_list = loadConfig(
            f"configs/{config_file}", f"configs/schemas/{schema_file}"
        )
        match (config_file):
            case "bluesky.json":
                for bot_conf in conf_list:
                    if bot_conf["enabled"]:
                        bot_client = BskyBot(
                            bot_conf["name"],
                            bot_conf["credentials"],
                            bot_conf["filepath"],
                        )
                        bot_client.post()
            case "twitter.json":
                for bot_conf in conf_list:
                    if bot_conf["enabled"]:
                        bot_client = TweetBot(
                            bot_conf["name"],
                            bot_conf["credentials"],
                            bot_conf["filepath"],
                            bot_conf["storage_threshold"],
                            bot_conf["chr_limit"],
                        )
                        bot_client.post()
