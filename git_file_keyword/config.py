import glob
import os
import pathlib
import typing

import git
import jieba_fast
from pydantic import BaseModel
from loguru import logger

from git_file_keyword import stopword
from git_file_keyword.exception import MaybeException


class ExtractConfig(BaseModel):
    depth: int = -1

    repo_root: pathlib.Path = pathlib.Path(".")
    file_list: typing.List[pathlib.Path] = []

    # if disabled, cache dir will be removed before run
    cache_enabled: bool = True

    # cutter
    cutter_func: typing.Callable[
        [str], typing.Iterable[str]
    ] = lambda x: jieba_fast.cut(x)
    stopword_set: typing.Set[str] = stopword.stopword_set
    ignore_low_freq_if_len: int = 20
    ignore_low_freq: int = 1

    # algo
    max_tfidf_feature_length: int = 20
    max_word_length: int = 32

    def verify(self) -> MaybeException:
        return self._verify_git() or self._verify_path()

    def _verify_git(self) -> MaybeException:
        try:
            _ = git.Repo(self.repo_root)
        except BaseException as e:
            return e
        self.repo_root = pathlib.Path(self.repo_root).resolve()

    def _verify_path(self) -> MaybeException:
        git_repo = git.Repo(self.repo_root)
        git_track_files = set([each[1].path for each in git_repo.index.iter_blobs()])

        if not self.file_list:
            logger.debug("file list is empty, use **/* instead")
            self.file_list = [
                pathlib.Path(each).resolve()
                for each in glob.glob(
                    os.path.join(self.repo_root, "**/*"), recursive=True
                )
            ]

        # file_list can be rel/abs
        real_file_list = []
        for each_file in self.file_list:
            each_file = pathlib.Path(each_file)
            if each_file.is_absolute():
                each_file = pathlib.Path(each_file).relative_to(self.repo_root)
            real_file_list.append(each_file)

        final = []
        for each_file in real_file_list:
            if not (self.repo_root / each_file).is_file():
                continue

            if each_file.as_posix() not in git_track_files:
                continue
            final.append(each_file)

        self.file_list = final
        return None
