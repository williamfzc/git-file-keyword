import git

from git_file_keyword.extractor import Extractor
from git_file_keyword.config import ExtractConfig


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

    config = ExtractConfig()
    config.repo_root = repo_path
    config.file_list = changed_files

    extractor = Extractor()
    result = extractor.extract(config)
    print(result.file_results)


if __name__ == "__main__":
    # Example usage
    repo_path = "../../jvm-sandbox"
    start_commit_ref = "HEAD~2"
    end_commit_ref = "HEAD"
    get_commits_diff(repo_path, start_commit_ref, end_commit_ref)
