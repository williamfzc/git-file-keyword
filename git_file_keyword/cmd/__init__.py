import csv
import glob
import os

import click

from git_file_keyword.extractor import Extractor


@click.command()
@click.option("--repo", default=".")
@click.option("--output_csv", default="./output.csv")
@click.option("--include", default="**")
@click.option("--stopword_txt", default="")
def main(repo: str, output_csv: str, include: str, stopword_txt: str):
    extractor = Extractor()
    extractor.config.repo_root = repo

    file_paths = glob.glob(os.path.join(repo, include), recursive=True)
    extractor.config.file_list = file_paths

    if stopword_txt:
        stopword_txt_list = stopword_txt.split(",")
        for each in stopword_txt_list:
            extractor.add_stopwords_file(each)

    result = extractor.extract()

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)

        for k, v in result.file_results.items():
            writer.writerow([k, *v.keywords])


if __name__ == "__main__":
    main()
