import csv
import glob
import os
import pathlib

from git_file_keyword.config import ExtractConfig
from git_file_keyword.extractor import Extractor

config = ExtractConfig()
config.repo_root = "../../jvm-sandbox"
extractor = Extractor(config)

for each_file in (
    "../assets/baidu_stopwords.txt",
    "../assets/cn_stopwords.txt",
    "../assets/thirdparty_stopwords.txt",
    "../assets/bd_stopwords.txt",
):
    if pathlib.Path(each_file).is_file():
        extractor.add_stopwords_file(each_file)

file_paths = glob.glob(os.path.join(config.repo_root, "**/*.java"), recursive=True)
file_paths = [file_path for file_path in file_paths if "node_modules" not in file_path]

file_paths = file_paths[:10]

config.file_list = [
    os.path.relpath(file_path, config.repo_root) for file_path in file_paths
]

extractor = Extractor(config)
result = extractor.extract()

with open("output.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["filepath", "keyword"])

    for k, v in result.file_results.items():
        words = ",".join(v.tfidf.keys())
        writer.writerow([k, words])


# with open("output.json", "w+", encoding="utf-8") as f:
#     f.write(result.model_dump_json())
