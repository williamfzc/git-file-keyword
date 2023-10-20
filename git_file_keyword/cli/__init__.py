import glob
import os
import pathlib

import click
from git_file_keyword.config import FileLevelEnum

from git_file_keyword.extractor import Extractor
from git_file_keyword.plugin_llm import OpenAILLMPlugin


@click.command()
@click.option("--repo", default=".")
@click.option("--output_csv", default="./output.csv")
@click.option("--include", default="**")
@click.option("--stopword_txt", default="")
@click.option("--openai_key", default="")
@click.option("--llm_rate_limit_wait", default="")
@click.option("--cache_enabled", default=True)
@click.option("--file_level")
def main(
        repo: str,
        output_csv: str,
        include: str,
        stopword_txt: str,
        openai_key: str,
        llm_rate_limit_wait: int,
        cache_enabled: bool,
        file_level: str,
):
    # gfk --include "**/*.py" --openai_key="sk-***"
    extractor = Extractor()

    repo = pathlib.Path(repo).resolve().absolute()
    extractor.config.repo_root = repo

    file_paths = glob.glob(os.path.join(repo.as_posix(), include), recursive=True)
    extractor.config.file_list = file_paths
    extractor.config.cache_enabled = cache_enabled
    extractor.config.file_level = file_level or FileLevelEnum.FILE

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
