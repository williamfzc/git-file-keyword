import os
import pathlib
import typing
from collections import defaultdict

import git
from loguru import logger

from git_file_keyword.config import ExtractConfig
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


class Extractor(_CacheBase):
    def extract(self) -> Result:
        err = self.config.verify()
        if err:
            raise err
        logger.info("config validation ok")

        repo = git.Repo(self.config.repo_root)

        # cache
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
        total = len(file_todo)
        for cur, file_result in enumerate(file_todo):
            kwargs = {
                "paths": file_result.path,
            }
            if self.config.depth != -1:
                kwargs["max_count"] = self.config.depth

            for commit in repo.iter_commits(**kwargs):
                file_result._commits.append(commit)

            self._extract_word_freq(file_result)
            logger.debug(f"progress: {cur + 1}/{total}")

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

    def _extract_word_freq(self, file_result: FileResult):
        word_freq = defaultdict(int)

        text = []
        for commit in file_result._commits:
            text.append(commit.message.strip())

        text_str = "\n".join(text)
        tokens = self.config.cutter_func(text_str)
        for each in tokens:
            name = strip_symbol(each.strip())
            if not name:
                continue

            # stopwords
            name = name.lower()
            if name in self.config.stopword_set:
                continue

            # too long
            if len(name) > self.config.max_word_length:
                continue

            word_freq[name] += 1

        logger.info(
            f"extract {file_result.path}, related commits: {len(file_result._commits)}, text: {len(text_str)}, token: {len(word_freq)}"
        )

        # reduce noice
        if len(word_freq) > self.config.ignore_low_freq_if_len:
            # remove all the words which called only once
            filtered_word_freq = {
                word: freq
                for word, freq in word_freq.items()
                if freq > self.config.ignore_low_freq
            }
            file_result.word_freq = filtered_word_freq
        else:
            file_result.word_freq = word_freq
