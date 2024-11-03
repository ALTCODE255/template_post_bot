import re
from io import BytesIO
from textwrap import dedent
from urllib.request import Request, urlopen

import atproto

from .PostBot import PostBot


class BskyBot(PostBot):
    def __init__(self, name: str, credentials: dict[str, str], source_file: str):
        super().__init__(name, credentials, source_file)

    def initClient(self):
        self.client = atproto.Client()
        self.client.login(
            self.credentials["user-handle"], self.credentials["app-password"]
        )

    def post(self):
        posts = self.getPosts()
        if self.validatePosts(posts):
            choice = super().getRandomPost(posts)
            img_pattern = r"(?:^|\s)getImage\[(.+?)]"
            post_text = re.sub(img_pattern, "", choice)
            post_images = []
            image_urls = [match[0] for match in re.findall(img_pattern, choice)]
            for url in image_urls:
                img_data = self.__getImage(url)
                if img_data:
                    post_images.append(img_data)
            try:
                self.initClient()
                if post_images:
                    self.client.send_images(text=post_text, images=post_images)
                elif post_text:
                    self.client.send_post(choice)
                else:
                    print(f"Attempted to send an invalid image post: '{choice}'")
                    print("Skipped:", self.name)
            except Exception as error:
                print(f"[{self.name}]", error)
        else:
            print("Skipped:", self.name)

    def getPosts(self) -> list[str]:
        try:
            return super().getPosts()
        except FileNotFoundError:
            default_text = dedent(
                """
            # Place possible posts for the script to select from here. There should be one per line. If you have 'multi-line' posts, write "\\n" where you want your line breaks to be.
            # The script will ignore any empty lines, as well as lines that are 'commented' out with a "#".
            # It is up to you to ensure that each post is at maximum 300 characters long.
            """
            )
            with open(self.source_file, "w+") as f:
                f.write(default_text)
            print(
                f"Source file '{self.source_file}' not found. A clean file has been generated for you."
            )
            return []

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
