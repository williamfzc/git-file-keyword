import hashlib
import pathlib
import re
from collections import defaultdict


def merge_word_freq(dict1, dict2):
    merged_dict = defaultdict(int)
    for word, freq in dict1.items():
        merged_dict[word] += freq
    for word, freq in dict2.items():
        merged_dict[word] += freq
    return merged_dict


def calc_checksum(fp: pathlib.Path):
    with fp.open(mode="rb") as f:
        hasher = hashlib.new("sha1", f.read())
        return hasher.hexdigest()


def strip_symbol(origin: str) -> str:
    return re.sub(r"[^\w\s]", "", origin)


def split_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
