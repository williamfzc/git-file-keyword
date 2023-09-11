"""
Extract the diff files only
"""
import subprocess

from git_file_keyword.config import ExtractConfig
from git_file_keyword.extractor import Extractor

config = ExtractConfig()
config.repo_root = ".."
config.cache_enabled = False

extractor = Extractor(config)
diff_command = ["git", "diff", "--name-only", "HEAD", "HEAD~1"]
output = subprocess.check_output(diff_command, cwd=config.repo_root).decode("utf-8")
file_list = output.strip().split("\n")
print(file_list)
config.file_list = file_list

result = extractor.extract()
result.export_csv("output.csv")
