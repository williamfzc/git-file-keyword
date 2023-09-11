import json

from git_file_keyword.config import ExtractConfig
from git_file_keyword.extractor import Extractor

config = ExtractConfig()
config.repo_root = ".."
extractor = Extractor(config)
result = extractor.extract()
output = result.export_global_word_freq()
with open("output.json", "w+") as f:
    json.dump(result.export_global_word_freq(), f)
