import pathlib
import typing

import git
import jieba_fast
from pydantic import BaseModel

from git_file_keyword.exception import MaybeException


class ExtractConfig(BaseModel):
    depth: int = -1

    repo_root: pathlib.Path = pathlib.Path(".")
    file_list: typing.List[pathlib.Path] = []

    # cutter
    cutter_func: typing.Callable[
        [str], typing.Iterable[str]
    ] = lambda x: jieba_fast.cut(x)
    stopword_set: typing.Set[str] = set()
    ignore_low_freq_if_len: int = 20
    ignore_low_freq: int = 1

    # algo
    max_tfidf_feature_length: int = 20
    max_word_length: int = 32

    def verify(self) -> MaybeException:
        return self._verify_path() or self._verify_git()

    def _verify_git(self) -> MaybeException:
        try:
            _ = git.Repo(self.repo_root)
        except BaseException as e:
            return e

    def _verify_path(self) -> MaybeException:
        root = pathlib.Path(self.repo_root)
        self.repo_root = root

        real_file_list = [pathlib.Path(each_file) for each_file in self.file_list]
        for each_file in real_file_list:
            if not (root / each_file).exists():
                return FileNotFoundError(each_file)
        self.file_list = real_file_list
        return None
