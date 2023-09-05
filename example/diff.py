import git

from git_file_keyword.config import ExtractConfig
from git_file_keyword.extractor import Extractor


def resolve_commit_sha(repo_path, commit_ref):
    repo = git.Repo(repo_path)
    commit = repo.commit(commit_ref)
    return commit.hexsha


def get_commits_diff(repo_path, start_commit_ref, end_commit_ref):
    start_commit_hex = resolve_commit_sha(repo_path, start_commit_ref)
    end_commit_hex = resolve_commit_sha(repo_path, end_commit_ref)

    repo = git.Repo(repo_path)
    start_commit = repo.commit(start_commit_hex)
    end_commit = repo.commit(end_commit_hex)

    # Get the list of changed files between start_commit and end_commit
    changed_files = [diff.b_path for diff in start_commit.diff(end_commit)]

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
    config.repo_root = repo_path
    config.file_list = changed_files
    config.stopword_set = stopwords

    extractor = Extractor()
    result = extractor.extract(config)
    with open("output.json", "w+", encoding="utf-8") as f:
        f.write(result.model_dump_json())


if __name__ == "__main__":
    # Example usage
    repo_path = ".."
    start_commit_ref = "HEAD~1"
    end_commit_ref = "HEAD"
    get_commits_diff(repo_path, start_commit_ref, end_commit_ref)
