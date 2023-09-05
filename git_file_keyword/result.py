import pathlib
import typing
from collections import defaultdict

from git import Commit
from pydantic import BaseModel


class FileResult(BaseModel):
    word_freq: typing.Dict[str, int] = dict()
    tfidf: typing.Dict = dict()

    _commits: typing.List[Commit] = []

    class Config:
        arbitrary_types_allowed = True


class Result(BaseModel):
    file_results: typing.Dict[pathlib.Path, FileResult] = defaultdict(FileResult)
