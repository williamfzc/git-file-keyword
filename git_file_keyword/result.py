import pathlib
import typing
from collections import defaultdict

from git import Commit
from pydantic import BaseModel


class FileResult(BaseModel):
    path: str = ""
    checksum: str = ""

    word_freq: typing.Dict[str, int] = dict()
    tfidf: typing.Dict[str, float] = dict()

    _commits: typing.List[Commit] = []

    class Config:
        arbitrary_types_allowed = True

    def clear(self):
        self.checksum = ""
        self.word_freq = dict()
        self.tfidf = dict()
        self._commits = []


class Result(BaseModel):
    file_results: typing.Dict[pathlib.Path, FileResult] = defaultdict(FileResult)
