import pathlib
import typing
from collections import defaultdict

from git import Commit
from pydantic import BaseModel


class FileResult(BaseModel):
    path: str = ""
    checksum: str = ""

    # raw
    word_freq: typing.Dict[str, int] = dict()
    _commits: typing.List[Commit] = []

    # final result
    keywords: typing.List[str] = list()

    # plugin output
    plugin_output: typing.Dict = dict()

    class Config:
        arbitrary_types_allowed = True


class Result(BaseModel):
    file_results: typing.Dict[pathlib.Path, FileResult] = defaultdict(FileResult)
