import git

from git_file_keyword.config import ExtractConfig
from git_file_keyword.result import Result


class Extractor(object):
    def extract(self, config: ExtractConfig) -> Result:
        err = config.verify()
        if err:
            raise err

        result = Result()
        repo = git.Repo(config.repo_root)
        diff_data = dict()
        for file_path in config.file_list:
            if file_path not in diff_data:
                diff_data[file_path] = []

            kwargs = {
                "paths": file_path,
            }
            if config.depth != -1:
                kwargs["max_count"] = config.depth

            for commit in repo.iter_commits(**kwargs):
                # what happened on this file in this commit
                result.file_results[file_path].commits.append(commit)

        return result
