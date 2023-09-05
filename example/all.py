import csv
import glob
import os

from git_file_keyword.config import ExtractConfig
from git_file_keyword.extractor import Extractor

stopwords = set()
for each_file in (
        "../assets/baidu_stopwords.txt",
        "../assets/cn_stopwords.txt",
        "../assets/thirdparty_stopwords.txt",
        "../assets/bd_stopwords.txt"
):
    with open(each_file) as f:
        lines = f.readlines()
        lines = [each.strip() for each in lines]
        stopwords = stopwords.union(set(lines))

config = ExtractConfig()
config.repo_root = ".."

file_paths = glob.glob(os.path.join(config.repo_root, '**/*.tsx'), recursive=True)
file_paths = [file_path for file_path in file_paths if 'node_modules' not in file_path]

file_paths = file_paths[:50]

config.file_list = [os.path.relpath(file_path, config.repo_root) for file_path in file_paths]
config.stopword_set = stopwords

extractor = Extractor()
result = extractor.extract(config)

with open('output.csv', 'w', newline='', encoding="utf-8-sig") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['filepath', 'keyword'])

    for k, v in result.file_results.items():
        words = ','.join(v.tfidf.keys())
        writer.writerow([k, words])


# with open("output.json", "w+", encoding="utf-8") as f:
#     f.write(result.model_dump_json())
