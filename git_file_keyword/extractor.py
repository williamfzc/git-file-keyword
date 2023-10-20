import os
import pathlib
import shutil
import typing
from collections import defaultdict

import git
from keybert import KeyBERT
from loguru import logger

from git_file_keyword.config import ExtractConfig, FileLevelEnum
from git_file_keyword.plugin import TfidfPlugin, BasePlugin
from git_file_keyword.result import Result, FileResult
from git_file_keyword.utils import calc_checksum, strip_symbol


class _ConfigBase(object):
    _plugins: typing.List[BasePlugin] = [
        TfidfPlugin(),
    ]

    def __init__(self, config: ExtractConfig = None):
        self.config = config or ExtractConfig()

    def add_stopwords_file(self, txt: str):
        txt_path = pathlib.Path(txt)
        assert txt_path.is_file()
        with txt_path.open() as f:
            lines = [each.strip() for each in f.readlines()]
            self.config.stopword_set = self.config.stopword_set.union(set(lines))

    def add_plugin(self, new_plugin: BasePlugin):
        self._plugins.append(new_plugin)


class _CacheBase(_ConfigBase):
    def get_cache_dir(self) -> pathlib.Path:
        # each git repo has its own .gfk_cache
        ret = self.config.repo_root / ".gfk_cache"
        ret.mkdir(exist_ok=True)
        return ret

    def get_cache_word_file(self) -> pathlib.Path:
        return self.get_cache_dir() / "word.txt"

    def write_fs(self, result: Result):
        word = self.get_cache_word_file()
        logger.debug(f"save result to cache: {word}")

        with open(word, "w+", encoding="utf-8") as f:
            for file_result in result.file_results.values():
                f.write(file_result.model_dump_json(exclude_unset=True) + os.linesep)

    def read_fs(self) -> typing.Optional[Result]:
        word = self.get_cache_word_file()
        logger.info(f"load result from cache: {word}")

        if not word.exists():
            return None

        result = Result()
        with open(word, "r", encoding="utf-8") as f:
            for line in f:
                file_result: FileResult = FileResult.model_validate_json(line.strip())
                result.file_results[pathlib.Path(file_result.path)] = file_result

        return result

    def clear_cache(self):
        # careful !!
        shutil.rmtree(self.get_cache_dir())


class Extractor(_CacheBase):
    def extract(self) -> Result:
        err = self.config.verify()
        if err:
            raise err
        logger.info("config validation ok")

        repo = git.Repo(self.config.repo_root)

        # cache
        if not self.config.cache_enabled:
            self.clear_cache()
        result = self.read_fs()
        if not result:
            logger.info("no cache found")
            result = Result()

        # check tasks
        file_todo: typing.List[FileResult] = []
        for file_path in self.config.file_list:
            if file_path not in result.file_results:
                # new file
                new_file_result = FileResult()
                file_todo.append(new_file_result)

                # result should be serializable
                new_file_result.path = file_path.as_posix()
                new_file_result.checksum = calc_checksum(
                    self.config.repo_root / file_path
                )
                result.file_results[file_path] = new_file_result
            else:
                # old file, check checksum
                cached_file_result = result.file_results[file_path]
                cur_checksum = calc_checksum(self.config.repo_root / file_path)
                if cached_file_result.checksum != cur_checksum:
                    # should be renewed
                    logger.info(f"{file_path} checksum mismatch, recalc")
                    new_file_result = FileResult()
                    new_file_result.path = file_path.as_posix()
                    new_file_result.checksum = cur_checksum
                    result.file_results[file_path] = new_file_result

        # word extract
        if self.config.file_level == FileLevelEnum.FILE:
            total = len(file_todo)
            for cur, file_result in enumerate(file_todo):
                kwargs = {
                    "paths": file_result.path,
                }
                if self.config.max_depth_limit != -1:
                    kwargs["max_count"] = self.config.max_depth_limit

                for commit in repo.iter_commits(**kwargs):
                    file_result._commits.append(commit)

                self._extract_word_freq_from_commits(file_result)
                logger.debug(f"progress: {cur + 1}/{total}, "
                             f"file: {file_result.path}, "
                             f"related commits: {len(file_result._commits)}, "
                             f"token: {len(file_result.word_freq)}")
        else:
            dir_dict: typing.Dict[str, typing.List[FileResult]] = dict()
            for each in file_todo:
                each_dir = os.path.dirname(each.path)
                if each_dir not in dir_dict:
                    dir_dict[each_dir] = []
                dir_dict[each_dir].append(each)

            cur = 0
            total = len(dir_dict)
            for each_dir, each_file_list in dir_dict.items():
                # extract once for each dir
                kwargs = {
                    "paths": each_dir,
                }
                if self.config.max_depth_limit != -1:
                    kwargs["max_count"] = self.config.max_depth_limit

                related_commits = []
                for commit in repo.iter_commits(**kwargs):
                    related_commits.append(commit)
                commit_msg_list = [
                    each_commit.message.strip()
                    for each_commit
                    in related_commits
                ]
                word_freq = self._extract_word_freq_from_docs(commit_msg_list)
                for each_file in each_file_list:
                    each_file._commits = related_commits
                    each_file.word_freq = word_freq
                logger.debug(f"progress: {cur + 1}/{total}, "
                             f"dir: {each_dir}, "
                             f"related commits: {len(related_commits)}")
                cur += 1

        # write cache
        self.write_fs(result)

        # apply plugins
        # in plugins, dev can decide using cache or not by `FileResult.cached`
        for each in self._plugins:
            each.apply(self.config, result)

        # update cache
        self.write_fs(result)

        logger.info("ok")
        return result

    def _extract_word_freq_from_docs(self, docs: typing.List[str]) -> dict:
        word_freq = defaultdict(int)
        tokens = set()

        # create model for extracting
        kw_model = KeyBERT(model=self.config.keybert_model)
        # supress warning
        os.putenv("TOKENIZERS_PARALLELISM", "False")
        # convert to list for keybert
        stopword_list = list(self.config.stopword_set)

        keywords_list = kw_model.extract_keywords(
            docs,
            stop_words=stopword_list,
            use_mmr=True,
            top_n=self.config.keybert_keyword_limit,
        )
        for each_keywords in keywords_list:
            if isinstance(each_keywords, tuple):
                tokens.add(each_keywords[0])
            else:
                for each_keyword in each_keywords:
                    tokens.add(each_keyword[0])

        for each in tokens:
            name = self.filter_name(each)
            if name:
                word_freq[name] += 1

        # reduce noice
        if len(word_freq) > self.config.ignore_low_freq_if_len:
            # remove all the words which called only once
            filtered_word_freq = {
                word: freq
                for word, freq in word_freq.items()
                if freq > self.config.ignore_low_freq
            }
            return filtered_word_freq

        return word_freq

    def _extract_word_freq_from_commits(self, file_result: FileResult):
        commit_msg_list = list()
        for commit in file_result._commits:
            commit_msg = commit.message.strip()
            commit_msg_list.append(commit_msg)

        word_freq = self._extract_word_freq_from_docs(commit_msg_list)
        file_result.word_freq = word_freq

    def filter_name(self, name: str) -> str:
        name = strip_symbol(name.strip())
        if not name:
            return ""

        # stopwords
        name = name.lower()
        if name in self.config.stopword_set:
            return ""

        # too long
        if len(name) > self.config.max_word_length:
            return ""

        # pure digit
        if name.isdigit():
            return ""

        return name
