import pathlib
import typing

import git
import jieba_fast
from pydantic import BaseModel

from git_file_keyword import stopword
from git_file_keyword.exception import MaybeException


class ExtractConfig(BaseModel):
    depth: int = -1

    repo_root: pathlib.Path = pathlib.Path(".")
    file_list: typing.List[pathlib.Path] = []

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
        self.repo_root = pathlib.Path(self.repo_root)

    def _verify_path(self) -> MaybeException:
        git_repo = git.Repo(self.repo_root)
        git_track_files = set([each[1].path for each in git_repo.index.iter_blobs()])

        real_file_list = [pathlib.Path(each_file).relative_to(self.repo_root) for each_file in self.file_list]

        final = []
        for each_file in real_file_list:
            if not (self.repo_root / each_file).is_file():
                continue

            if each_file.as_posix() not in git_track_files:
                continue
            final.append(each_file)

        self.file_list = final
        return None
