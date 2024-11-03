import random
import re
from abc import ABC, abstractmethod
from typing import Any


class PostBot(ABC):
    @abstractmethod
    def __init__(self, name: str, credentials: dict[str, str], source_file: str):
        self.name = name
        self.client = self.initClient(credentials)
        self.source_file = source_file

    @abstractmethod
    def initClient(self, credentials: dict[str, str]) -> Any:
        pass

    @abstractmethod
    def post(self):
        pass

    def getRandomPost(self, posts: list[str]) -> str:
        return random.choice(posts)

    def getPosts(self) -> list[str]:
        with open(self.source_file, "r", encoding="utf-8") as f:
            return [
                post.replace("\\n", "\n")
                for post in re.findall(
                    r"^(?!#.*$)\S.*", f.read().strip("\n"), re.MULTILINE
                )
            ]

    @abstractmethod
    def validatePosts(self, posts: list[str]) -> bool:
        pass
