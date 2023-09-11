"""
This script is usually used for extracting stopwords from global word dict.
"""
from git_file_keyword.config import ExtractConfig
from git_file_keyword.extractor import Extractor

config = ExtractConfig()
config.repo_root = ".."
config.cache_enabled = False

extractor = Extractor(config)
result = extractor.extract()

items = result.export_global_word_freq().items()
sorted_items = sorted(items, key=lambda x: x[1], reverse=True)
for item in sorted_items:
    print(item[0], item[1])
