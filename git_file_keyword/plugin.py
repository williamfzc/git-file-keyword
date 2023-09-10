from collections import OrderedDict

from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer

from git_file_keyword.config import ExtractConfig
from git_file_keyword.result import Result


class BasePlugin(object):
    # modify in place
    def apply(self, config: ExtractConfig, result: Result):
        raise NotImplemented

    def plugin_id(self) -> str:
        raise NotImplemented


class TfidfPlugin(BasePlugin):
    def apply(self, config: ExtractConfig, result: Result):
        logger.info("calc tfidf ...")
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

            sorted_indices = tfidf_scores.argsort()[::-1][
                : config.max_tfidf_feature_length
            ]
            cur_tfidf_dict = dict()
            for index in sorted_indices:
                word = feature_names[nonzero_indices[index]]
                score = tfidf_scores[index]
                cur_tfidf_dict[word] = score

            cur_file_result = result.file_results[document_name]
            cur_file_result.keywords = list(cur_tfidf_dict.keys())
            cur_file_result.plugin_output[self.plugin_id()] = cur_tfidf_dict

    def plugin_id(self) -> str:
        return "tf-idf"
