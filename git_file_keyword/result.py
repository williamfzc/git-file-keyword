import csv
import pathlib
import typing
from collections import defaultdict

from git import Commit
from pydantic import BaseModel


class FileResult(BaseModel):
    path: str = ""
    checksum: str = ""
    cached: bool = False

    # raw
    word_freq: typing.Dict[str, int] = dict()
    _commits: typing.List[Commit] = []

    # final result
    keywords: typing.List[str] = list()
    description: str = ""

    # plugin output
    plugin_output: typing.Dict = dict()

    class Config:
        arbitrary_types_allowed = True


class Result(BaseModel):
    file_results: typing.Dict[pathlib.Path, FileResult] = defaultdict(FileResult)

    def export_csv(self, path: str):
        with open(path, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile)

            # header
            writer.writerow(["File", "Keywords", "Description"])
            for k, v in self.file_results.items():
                writer.writerow([k, "|".join(v.keywords), v.description or "N/A"])

    def export_global_word_freq(self) -> dict:
        merged_freq = dict()
        for v in self.file_results.values():
            for word, count in v.word_freq.items():
                merged_freq[word] = merged_freq.get(word, 0) + count
        return merged_freq
