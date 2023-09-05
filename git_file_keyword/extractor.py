from collections import defaultdict, OrderedDict

import git
import pkuseg
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer

from git_file_keyword.config import ExtractConfig
from git_file_keyword.result import Result, FileResult


def merge_word_freq(dict1, dict2):
    merged_dict = defaultdict(int)
    for word, freq in dict1.items():
        merged_dict[word] += freq
    for word, freq in dict2.items():
        merged_dict[word] += freq
    return merged_dict


class Extractor(object):
    def extract(self, config: ExtractConfig) -> Result:
        err = config.verify()
        if err:
            raise err

        result = Result()
        repo = git.Repo(config.repo_root)
        for file_path in config.file_list:
            cur_file_result = result.file_results[file_path]

            kwargs = {
                "paths": file_path,
            }
            if config.depth != -1:
                kwargs["max_count"] = config.depth

            for commit in repo.iter_commits(**kwargs):
                cur_file_result._commits.append(commit)
            self._extract_word_freq(cur_file_result, config)

        # tf-idf
        self._calculate_tfidf(result, config)
        return result

    def _extract_word_freq(self, file_result: FileResult, config: ExtractConfig):
        word_freq = defaultdict(int)
        seg = pkuseg.pkuseg(postag=True)

        for commit in file_result._commits:
            tokens = seg.cut(commit.message.strip())
            for each in tokens:
                name, characteristic = each[0], each[1]

                # stopwords
                if name in config.stopword_set:
                    continue

                # only noun, but current segment is not good enough
                if "n" in characteristic:
                    word_freq[name] += 1

        # reduce noice
        if len(word_freq) > config.ignore_low_freq_if_len:
            # remove all the words which called only once
            filtered_word_freq = {word: freq for word, freq in word_freq.items() if freq > config.ignore_low_freq}
            file_result.word_freq = filtered_word_freq
        else:
            file_result.word_freq = word_freq

    def _calculate_tfidf(self, result: Result, config: ExtractConfig):
        # vocabulary
        documents = {
            k: ' '.join([word for word, freq in v.word_freq.items() for _ in range(freq)])
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

            sorted_indices = tfidf_scores.argsort()[::-1][:config.max_tfidf_limit]
            cur_tfidf_dict = dict()
            for index in sorted_indices:
                word = feature_names[nonzero_indices[index]]
                score = tfidf_scores[index]
                cur_tfidf_dict[word] = score

            result.file_results[document_name].tfidf = cur_tfidf_dict
