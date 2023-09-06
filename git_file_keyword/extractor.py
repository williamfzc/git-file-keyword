import pathlib
from collections import defaultdict, OrderedDict

import git
import jieba_fast as jieba
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer

from git_file_keyword.config import ExtractConfig
from git_file_keyword.result import Result, FileResult


class _ConfigBase(object):
    def __init__(self, config: ExtractConfig = None):
        self.config = config or ExtractConfig()

    def add_stopwords_file(self, txt: str):
        txt_path = pathlib.Path(txt)
        assert txt_path.is_file()
        with txt_path.open() as f:
            lines = [each.strip() for each in f.readlines()]
            self.config.stopword_set = self.config.stopword_set.union(set(lines))


class Extractor(_ConfigBase):
    def extract(self) -> Result:
        err = self.config.verify()
        if err:
            raise err
        logger.info("config validation ok")

        result = Result()
        repo = git.Repo(self.config.repo_root)

        # words from commit msg
        for file_path in self.config.file_list:
            cur_file_result = result.file_results[file_path]
            cur_file_result.path = file_path

            kwargs = {
                "paths": file_path,
            }
            if self.config.depth != -1:
                kwargs["max_count"] = self.config.depth

            for commit in repo.iter_commits(**kwargs):
                cur_file_result._commits.append(commit)

            self._extract_word_freq(cur_file_result)

        # tf-idf
        logger.info("calc tfidf ...")
        self._calculate_tfidf(result)

        logger.info("ok")
        return result

    def _extract_word_freq(self, file_result: FileResult):
        word_freq = defaultdict(int)

        text = []
        for commit in file_result._commits:
            text.append(commit.message.strip())

        text_str = "\n".join(text)
        tokens = jieba.cut(text_str)
        for each in tokens:
            name = each.strip()

            # stopwords
            if name in self.config.stopword_set:
                continue

            # too long
            if len(name) > self.config.max_word_length:
                continue

            word_freq[name] += 1

        logger.info(
            f"extract {file_result.path}, related commits: {len(file_result._commits)}, text: {len(text_str)}, token: {len(word_freq)}")

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

    def _calculate_tfidf(self, result: Result):
        # vocabulary
        documents = {
            k: " ".join(
                [word for word, freq in v.word_freq.items() for _ in range(freq)]
            )
            for k, v in result.file_results.items()
            if v.word_freq
        }
        documents = OrderedDict(sorted(documents.items()))

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents.values())
        feature_names = vectorizer.get_feature_names_out()

        for document_name, tfidf_vector in zip(documents.keys(), tfidf_matrix):
            nonzero_indices = tfidf_vector.nonzero()[1]
            tfidf_scores = tfidf_vector.data

            sorted_indices = tfidf_scores.argsort()[::-1][: self.config.max_tfidf_feature_length]
            cur_tfidf_dict = dict()
            for index in sorted_indices:
                word = feature_names[nonzero_indices[index]]
                score = tfidf_scores[index]
                cur_tfidf_dict[word] = score

            result.file_results[document_name].tfidf = cur_tfidf_dict
