import pathlib
import typing
from collections import defaultdict

from git import Commit
from pydantic import BaseModel


class FileResult(BaseModel):
    commits: typing.List[Commit] = []

    class Config:
        exclude = {"commits"}
        arbitrary_types_allowed = True


class Result(BaseModel):
    file_results: typing.Dict[pathlib.Path, FileResult] = defaultdict(FileResult)
