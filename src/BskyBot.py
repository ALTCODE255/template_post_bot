import re
from io import BytesIO
from urllib.request import Request, urlopen

import atproto

from .PostBot import PostBot


class BskyBot(PostBot):
    def __init__(
        self, name: str, credentials: dict[str, str], source_file: str, log_thres: str
    ):
        super().__init__(name, credentials, source_file, log_thres)

    @property
    def SCHEMA_NAME(self) -> str:
        return "Bluesky"

    @property
    def DEFAULT_FILE_TEXT(self) -> str:
        return """
            # Place possible posts for the script to select from here. There should be one per line. If you have 'multi-line' posts, write "\n" where you want your line breaks to be.
            # The script will ignore any empty lines, as well as lines that are 'commented' out with a "#".
            # It is up to you to ensure that each post is at maximum 300 characters long.
            # To include images, begin a line with "getImage[url]". url should directly link to an image, and should not be enclosed in quotes. You can repeat this for up to four times at the beginning of a line, one per image.
            """

    def initClient(self):
        self.client = atproto.Client()
        self.client.login(
            self.credentials["user-handle"], self.credentials["app-password"]
        )

    def _postLogic(self, post) -> bool:
        img_pattern = r"(?:^|\s)getImage\[(.+?)]"
        post_text = re.sub(img_pattern, "", post)
        post_images = []
        image_urls = [match[0] for match in re.findall(img_pattern, post)]
        for url in image_urls:
            img_data = self.__getImage(url)
            if img_data:
                post_images.append(img_data)
        try:
            self.initClient()
            if post_images:
                self.client.send_images(text=post_text, images=post_images)
                return True
            elif post_text:
                self.client.send_post(post)
                return True
            else:
                print(f"Attempted to send an invalid image post: '{post}'")
                return False
        except Exception as error:
            print(f"[{self.name}]", error)
            return False

    def validatePosts(self, posts: list[str]) -> bool:
        if not posts:
            print(
                f"File has no valid posts. Please write at least one post in '{self.source_file}'.",
            )
            return False
        exceeding_imgs = [
            p for p in posts if len(re.findall(r"(?:^|\s)getImage\[(.+?)]", p)) > 4
        ]
        if exceeding_imgs:
            print(
                f"One or more posts in '{self.source_file}' contain too many images (max 4):\n-",
                "\n- ".join(exceeding_imgs),
            )
            return False
        exceeding_posts = [p for p in posts if len(p) > 300]
        if exceeding_posts:
            print(
                f"One or more posts in '{self.source_file}' exceeds the character limit (300):\n-",
                "\n- ".join(exceeding_posts),
            )
            return False
        return True

    def __getImage(self, url: str) -> BytesIO | None:
        r = Request(url, headers={"User-Agent": "Mozilla"})
        img_data = urlopen(r).read()
        if len(img_data) < 1000000:
            return img_data
        print(f"Image file size is too large. 1000000 bytes max, got: {len(img_data)}")
