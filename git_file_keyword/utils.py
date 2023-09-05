from collections import defaultdict


def merge_word_freq(dict1, dict2):
    merged_dict = defaultdict(int)
    for word, freq in dict1.items():
        merged_dict[word] += freq
    for word, freq in dict2.items():
        merged_dict[word] += freq
    return merged_dict
