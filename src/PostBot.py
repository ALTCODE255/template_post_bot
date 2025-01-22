import random
import re
from abc import ABC, abstractmethod
import sqlite3
from contextlib import closing
from textwrap import dedent


class PostBot(ABC):
    @abstractmethod
    def __init__(
        self,
        name: str,
        credentials: dict[str, str],
        source_file: str,
        log_thres: int,
    ):
        self.name = name
        self.credentials = credentials
        self.source_file = source_file
        self.log_thres = log_thres

    @property
    @abstractmethod
    def SCHEMA_NAME(self) -> str:
        pass

    @property
    @abstractmethod
    def DEFAULT_FILE_TEXT(self) -> str:
        pass

    @abstractmethod
    def initClient(self):
        pass

    @abstractmethod
    def validatePosts(self, posts: list[str]) -> bool:
        pass

    @abstractmethod
    def _postLogic(self, post: str) -> bool:
        # self.initClient()
        # self.client.post(post)
        # error handling etc. return True if no errors
        pass

    def post(self):
        posts = self.getPosts()
        if posts and self.validatePosts(posts):
            choice = self.getRandomPost(posts)
            success = self._postLogic(choice)
            if success:
                self.__addToRecent(choice)
                self.__clearOldRecent()
            else:
                print(f"[{self.SCHEMA_NAME}] Skipped:", self.name)
        else:
            print(f"[{self.SCHEMA_NAME}] Skipped:", self.name)

    def getRandomPost(self, posts: list[str]) -> str:
        return random.choice(posts)

    def getPosts(self) -> list[str]:
        try:
            with open(self.source_file, "r", encoding="utf-8") as f:
                log = self.__getRecent()
                return [
                    post.replace("\\n", "\n")
                    for post in re.findall(
                        r"^(?!#.*$)\S.*", f.read().strip("\n"), re.MULTILINE
                    )
                    if post.replace("\\n", "\n") not in log
                ]
        except FileNotFoundError:
            default_text = dedent(self.DEFAULT_FILE_TEXT)
            with open(self.source_file, "w+") as f:
                f.write(default_text)
            print(
                f"Source file '{self.source_file}' not found. A clean file has been generated for you."
            )
            return []

    def __getRecent(self) -> list[str]:
        if self.log_thres > 0:
            with closing(sqlite3.connect("recent.db")) as conn, conn:
                conn.execute(
                    """
                        CREATE TABLE IF NOT EXISTS RecentPosts (
                            id INTEGER,
                            schema TEXT NOT NULL,
                            name TEXT NOT NULL,
                            timestamp TEXT DEFAULT (DATETIME('now')),
                            text TEXT NOT NULL,
                            PRIMARY KEY(id AUTOINCREMENT)
                        )
                    """
                )
                recent = conn.execute(
                    """
                        SELECT text
                        FROM RecentPosts
                        WHERE name = ?
                        AND schema = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """,
                    [self.name, self.SCHEMA_NAME, self.log_thres],
                ).fetchall()
        if not self.log_thres or not recent:
            return []
        return [row[0] for row in recent]

    def __addToRecent(self, post: str):
        with closing(sqlite3.connect("recent.db")) as conn, conn:
            conn.execute(
                """
                    INSERT INTO RecentPosts (name, text, schema)
                    VALUES (?, ?, ?)
                """,
                [self.name, post, self.SCHEMA_NAME],
            )

    def __clearOldRecent(self):
        with closing(sqlite3.connect("recent.db")) as conn, conn:
            conn.execute(
                """
                    DELETE FROM RecentPosts
                    WHERE name = ?
                    AND schema = ?
                    AND id NOT IN (
                        SELECT id FROM RecentPosts
                        WHERE name = ? AND schema = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    )
                """,
                [
                    self.name,
                    self.SCHEMA_NAME,
                    self.name,
                    self.SCHEMA_NAME,
                    self.log_thres,
                ],
            )
