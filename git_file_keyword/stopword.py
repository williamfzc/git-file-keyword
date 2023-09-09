from nltk.corpus import stopwords

git_op_words = [
    "git",
    "repository",
    "commit",
    "branch",
    "merge",
    "pull",
    "push",
    "clone",
    "fetch",
    "checkout",
    "rebase",
    "stash",
    "tag",
    "remote",
    "origin",
    "upstream",
    "conflict",
    "ignore",
    "diff",
    "log",
    "status",
    "add",
    "remove",
    "reset",
    "amend",
    "blame",
    "cherry-pick",
    "grep",
    "reflog",
    "submodule",
    "ignore",
    "ignorecase",
    "ignore-space-change",
    "ignore-all-space",
    "ignore-blank-lines",
    "ignore-submodules",
    "ignore-missing",
    "ignore-errors",
    "ignore-paths",
    "ignore-paths-file",
    "ignore-other-worktrees",
    "ignore-skip-worktree-bits",
    "ignore-untracked",
    "ignore-non-option",
    "ignored",
    "ignore-space-at-eol",
    "ignore-space-change",
    "ignore-space-change-at-eol",
    "ignore-whitespace",
    "ignore-blank-lines-at-eof",
]

angular_commit_types = [
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
]


def gen_stopword_set() -> set:
    basic_words = set(stopwords.words("english"))
    return basic_words.union(git_op_words, angular_commit_types)


stopword_set = gen_stopword_set()
