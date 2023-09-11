import glob
import os

import click

from git_file_keyword.extractor import Extractor
from git_file_keyword.plugin_llm import OpenAILLMPlugin


@click.command()
@click.option("--repo", default=".")
@click.option("--output_csv", default="./output.csv")
@click.option("--include", default="**")
@click.option("--stopword_txt", default="")
@click.option("--openai_key", default="")
@click.option("--llm_rate_limit_wait", default="")
def main(
    repo: str,
    output_csv: str,
    include: str,
    stopword_txt: str,
    openai_key: str,
    llm_rate_limit_wait: int,
):
    # gfk --include "**/*.py" --openai_key="sk-***"
    extractor = Extractor()
    extractor.config.repo_root = repo

    file_paths = glob.glob(os.path.join(repo, include), recursive=True)
    extractor.config.file_list = file_paths

    if stopword_txt:
        stopword_txt_list = stopword_txt.split(",")
        for each in stopword_txt_list:
            extractor.add_stopwords_file(each)

    if openai_key:
        # enable llm enhancement
        openai_plugin = OpenAILLMPlugin()
        openai_plugin.token = openai_key
        extractor.add_plugin(openai_plugin)

        if llm_rate_limit_wait:
            openai_plugin.rate_limit_wait = llm_rate_limit_wait

    result = extractor.extract()
    result.export_csv(output_csv)


if __name__ == "__main__":
    main()
